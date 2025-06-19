import discord
from discord.commands import Option # Import thêm Option để định nghĩa tham số
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- CẤU HÌNH ---
import os # Import thêm thư viện os
# Lấy token từ biến môi trường của Railway thay vì ghi thẳng vào code
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") 
WEBSITE_URL = "https://rblx.earth/"

# --- KHỞI TẠO SELENIUM (CẬP NHẬT CHO SERVER) ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # BẮT BUỘC: Chạy ở chế độ không giao diện
options.add_argument("--no-sandbox") # BẮT BUỘC: Cần thiết để chạy Chrome trong môi trường container
options.add_argument("--disable-dev-shm-usage") # BẮT BUỘC: Tránh lỗi tài nguyên
options.add_argument("--disable-gpu") # Tùy chọn: Vô hiệu hóa GPU
options.add_argument("window-size=1920,1080") # Tùy chọn: Đặt kích thước cửa sổ ảo

# Khi dùng Docker, chúng ta không cần chỉ định đường dẫn tới chromedriver nữa
driver = webdriver.Chrome(options=options)

# --- KHỞI TẠO BOT DISCORD ---
intents = discord.Intents.default()
bot = commands.Bot(intents=intents) # Bỏ phần command_prefix

@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {bot.user}')
    print('Sẵn sàng nhận lệnh gạch chéo (/).')

# --- CÁC LỆNH GẠCH CHÉO CỦA BOT ---

@bot.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
async def start_rblx(
    ctx: discord.ApplicationContext, 
    roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
):
    """Lệnh /start: Mở web và liên kết tài khoản."""
    await ctx.defer() # Báo cho Discord biết bot cần thời gian xử lý

    try:
        await ctx.followup.send(f"Đang mở `{WEBSITE_URL}` và tìm ô nhập liệu...")
        driver.get(WEBSITE_URL)

        user_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )
        await ctx.followup.send(f"Đã tìm thấy ô nhập liệu. Đang liên kết tài khoản `{roblox_username}`...")
        user_field.send_keys(roblox_username)

        link_button = driver.find_element(By.XPATH, '//button[contains(text(), "Link Account")]')
        link_button.click()
        
        await ctx.followup.send("Đã gửi yêu cầu liên kết. Đang đợi trang tải...")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "sidebar-link") and .//span[text()="Earn"]]'))
        )
        
        # Sửa tin nhắn đầu tiên thành thông báo thành công
        await ctx.edit(content=f"✅ Đã liên kết tài khoản `{roblox_username}` thành công và đang ở trang chính!")

    except Exception as e:
        await ctx.edit(content=f"❌ Lỗi khi khởi động hoặc liên kết tài khoản: `{e}`")

@bot.slash_command(name="promo", description="Nhập mã khuyến mãi (promocode) trên rblx.earth.")
async def enter_promo(
    ctx: discord.ApplicationContext,
    code: Option(str, "Mã khuyến mãi bạn muốn nhập.", required=True)
):
    """Lệnh /promo: Nhập mã khuyến mãi."""
    await ctx.defer()
        
    try:
        await ctx.followup.send("Đang điều hướng đến trang `Promocodes`...")
        promo_page_link = driver.find_element(By.XPATH, '//a[contains(@href, "/promocodes")]')
        promo_page_link.click()

        await ctx.followup.send(f"Đang nhập mã `{code}`...")
        promo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
        )
        promo_field.send_keys(code)
        
        redeem_button = driver.find_element(By.XPATH, '//button[contains(text(), "Redeem")]')
        redeem_button.click()

        time.sleep(2)
        result_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'swal2-title'))
        )
        result_message = result_popup.text
        
        await ctx.edit(content=f"✅ Kết quả nhập mã: **{result_message}**")

    except Exception as e:
        await ctx.edit(content=f"❌ Lỗi khi nhập mã khuyến mãi: `{e}`")

@bot.slash_command(name="stop", description="Đóng trình duyệt web mà bot đang điều khiển.")
async def stop_browser(ctx: discord.ApplicationContext):
    """Lệnh /stop: Đóng trình duyệt."""
    await ctx.defer()
    try:
        await ctx.followup.send("Đang đóng trình duyệt...")
        driver.quit()
        await ctx.edit(content="✅ Đã đóng trình duyệt. Hẹn gặp lại!")
    except Exception as e:
        await ctx.edit(content=f"❌ Lỗi khi đóng trình duyệt: `{e}`")

# --- CHẠY BOT ---
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường.")
