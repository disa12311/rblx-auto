# === rblx_bot.py - Phiên bản tối ưu toàn bộ ===

import discord
from discord.commands import Option
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# --- CẤU HÌNH ---
# Lấy token từ biến môi trường của Railway, an toàn và đúng chuẩn.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBSITE_URL = "https://rblx.earth/"

# --- KHỞI TẠO SELENIUM ---
# Cấu hình các tùy chọn cho Chrome để chạy ổn định trong môi trường Docker/Server
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")

# Khởi tạo driver, Selenium sẽ tự tìm chromedriver trong PATH của container
driver = webdriver.Chrome(options=options)

# --- KHỞI TẠO BOT DISCORD ---
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

# --- CÁC HÀM XỬ LÝ LỖI ---
async def handle_error(ctx: discord.ApplicationContext, error: Exception, command_name: str):
    """Hàm xử lý lỗi tập trung để tránh lặp code và cho trải nghiệm người dùng tốt hơn."""
    # Ghi log lỗi chi tiết để chủ bot debug trên Railway
    print(f"CRITICAL ERROR in /{command_name}: {error}")
    # Gửi một thông báo thân thiện và ngắn gọn đến người dùng trên Discord
    await ctx.edit(content=(
        f"❌ **Đã có lỗi xảy ra khi thực thi lệnh `/{command_name}`!**\n"
        "Vui lòng thử lại sau. Nếu lỗi vẫn tiếp diễn, có thể website đã thay đổi hoặc bot đang được bảo trì."
    ))

# --- SỰ KIỆN KHI BOT SẴN SÀNG ---
@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {bot.user}')
    print('Bot đã sẵn sàng nhận lệnh. Trạng thái: Online 24/7 trên Railway.')

# --- CÁC LỆNH GẠCH CHÉO CỦA BOT ---

@bot.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
async def start_rblx(
    ctx: discord.ApplicationContext,
    roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
):
    await ctx.defer()
    try:
        if not roblox_username or not isinstance(roblox_username, str):
            await ctx.edit(content=f"❌ Lỗi: Tên người dùng Roblox không hợp lệ. Vui lòng thử lại.")
            return

        print(f"Executing /start for user: {roblox_username}")
        await ctx.followup.send(f"Đang mở `{WEBSITE_URL}` và chuẩn bị liên kết...")

        driver.get(WEBSITE_URL)
        user_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )
        
        driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
        
        link_button = driver.find_element(By.XPATH, '//button[contains(text(), "Link Account")]')
        link_button.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-balance"))
        )
        await ctx.edit(content=f"✅ **Thành công!** Đã liên kết tài khoản `{roblox_username}`.")

    except Exception as e:
        await handle_error(ctx, e, "start")

@bot.slash_command(name="promo", description="Nhập mã khuyến mãi (promocode) trên rblx.earth.")
async def enter_promo(
    ctx: discord.ApplicationContext,
    code: Option(str, "Mã khuyến mãi bạn muốn nhập.", required=True)
):
    await ctx.defer()
    try:
        print(f"Executing /promo with code: {code}")
        await ctx.followup.send("Đang điều hướng đến trang `Promocodes`...")
        
        promo_page_link = driver.find_element(By.XPATH, '//a[contains(@href, "/promocodes")]')
        promo_page_link.click()

        promo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
        )
        driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
        
        redeem_button = driver.find_element(By.XPATH, '//button[contains(text(), "Redeem")]')
        redeem_button.click()

        result_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'swal2-title'))
        )
        await ctx.edit(content=f"✅ **Kết quả nhập mã `{code}`:** {result_popup.text}")
        
    except Exception as e:
        await handle_error(ctx, e, "promo")

@bot.slash_command(name="balance", description="Kiểm tra số dư Robux hiện tại của bạn trên rblx.earth.")
async def check_balance(ctx: discord.ApplicationContext):
    await ctx.defer()
    try:
        print("Executing /balance")
        # Đi đến trang chủ để đảm bảo có thể thấy số dư
        driver.get(f"{WEBSITE_URL}earn")
        
        balance_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-balance"))
        )
        balance_text = balance_element.find_element(By.TAG_NAME, "span").text
        
        await ctx.edit(content=f"💰 **Số dư hiện tại của bạn là:** `{balance_text}`")

    except Exception as e:
        await handle_error(ctx, e, "balance")

# --- CHẠY BOT ---
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("CRITICAL: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")
