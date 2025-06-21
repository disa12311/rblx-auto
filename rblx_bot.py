import discord
from discord.commands import Option
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service # Vẫn cần để khởi tạo Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import asyncio # Để dùng await asyncio.sleep nếu cần

# --- CẤU HÌNH ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"

# --- CÁC TÙY CHỌN CHO CHROME (GLOBAL) ---
# Hàm này định nghĩa các tùy chọn cho Chrome
def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")              # Chạy không giao diện
    options.add_argument("--no-sandbox")            # Cần thiết cho môi trường container
    options.add_argument("--disable-dev-shm-usage") # Tránh lỗi tài nguyên
    options.add_argument("--disable-gpu")           # Tắt GPU
    options.add_argument("window-size=1920,1080")   # Giả lập kích thước màn hình
    # Thêm một số args khác thường giúp ổn định trên Linux/Docker
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3") # Chỉ hiển thị lỗi nghiêm trọng từ Chrome/WebDriver
    options.add_argument("--disable-logging") # Tắt logging của Chrome
    return options

# --- KHỞI TẠO BOT DISCORD ---
intents = discord.Intents.default()
# intents.message_content = True # Bật nếu bot cần đọc nội dung tin nhắn không phải slash command
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập với tên: {bot.user} vào lúc {discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print('✅ Sẵn sàng nhận lệnh gạch chéo (/).')

# --- CÁC LỆNH GẠCH CHÉO CỦA BOT ---

@bot.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
async def start_rblx(
    ctx: discord.ApplicationContext,
    roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
):
    await ctx.defer() # Báo cho Discord biết bot đang xử lý

    driver = None # Khởi tạo driver là None
    try:
        print(f"DEBUG: Lệnh /start nhận được từ {ctx.author}. Username: '{roblox_username}', Kiểu: {type(roblox_username)}")

        if not roblox_username or not isinstance(roblox_username, str):
            await ctx.followup.send(f"❌ Lỗi: Tên người dùng Roblox ('{roblox_username}') không hợp lệ. Vui lòng thử lại.")
            return

        await ctx.followup.send("⏳ Đang khởi tạo trình duyệt và tải trang...")

        # KHÔNG CẦN webdriver_manager.chromedriver.install() nữa!
        # Vì Dockerfile đã tự động tải và đặt ChromeDriver vào PATH.
        # Selenium sẽ tự tìm thấy nó.
        driver = webdriver.Chrome(options=get_chrome_options())

        driver.get(WEBSITE_URL)
        print(f"DEBUG: Đã tải URL: {WEBSITE_URL}")

        user_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )
        print("DEBUG: Đã tìm thấy ô nhập liệu.")
        await ctx.followup.send(f"➡️ Đã tìm thấy ô nhập liệu. Đang liên kết tài khoản `{roblox_username}`...")

        driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
        print(f"DEBUG: Đã nhập username: {roblox_username}")
        
        link_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Link Account")]'))
        )
        link_button.click()
        print("DEBUG: Đã click nút 'Link Account'.")
        
        await ctx.followup.send("⌛ Đã gửi yêu cầu liên kết. Đang đợi trang chính tải...")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "sidebar-link") and .//span[text()="Earn"]]'))
        )
        print("DEBUG: Đã tải trang chính thành công.")
        
        await ctx.edit(content=f"✅ Đã liên kết tài khoản `{roblox_username}` thành công và đang ở trang chính!")

    except Exception as e:
        print(f"❌ Lỗi trong lệnh /start: {e}")
        await ctx.edit(content=f"❌ Đã xảy ra lỗi khi thực thi lệnh /start: `{e}`")
    finally:
        if driver:
            driver.quit()
            print("DEBUG: Trình duyệt đã đóng.")

@bot.slash_command(name="promo", description="Nhập mã khuyến mãi (promocode) trên rblx.earth.")
async def enter_promo(
    ctx: discord.ApplicationContext,
    code: Option(str, "Mã khuyến mãi bạn muốn nhập.", required=True)
):
    await ctx.defer()
    driver = None
    try:
        print(f"DEBUG: Lệnh /promo nhận được từ {ctx.author}. Code: '{code}'")

        await ctx.followup.send("⏳ Đang khởi tạo trình duyệt và tải trang Promocodes...")
        
        driver = webdriver.Chrome(options=get_chrome_options())
        driver.get(WEBSITE_URL) # Tải lại trang web chính trước
        print(f"DEBUG: Đã tải URL chính: {WEBSITE_URL}")

        # Đợi trang tải xong trước khi điều hướng tới promocodes
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )

        promo_page_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/promocodes")]'))
        )
        promo_page_link.click()
        print("DEBUG: Đã click vào link 'Promocodes'.")

        await ctx.followup.send(f"➡️ Đang nhập mã `{code}`...")
        
        promo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
        )
        driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
        print(f"DEBUG: Đã nhập mã khuyến mãi: {code}")
        
        redeem_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Redeem")]'))
        )
        redeem_button.click()
        print("DEBUG: Đã click nút 'Redeem'.")

        result_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'swal2-title'))
        )
        result_message = result_popup.text
        print(f"DEBUG: Kết quả pop-up: {result_message}")
        
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
            )
            ok_button.click()
            await asyncio.sleep(0.5) # Chờ một chút để pop-up biến mất hoàn toàn
            print("DEBUG: Đã click nút 'OK' trên pop-up.")
        except:
            print("DEBUG: Không tìm thấy nút 'OK' hoặc pop-up tự đóng.")
            pass

        await ctx.edit(content=f"✅ Kết quả nhập mã: **{result_message}**")

    except Exception as e:
        print(f"❌ Lỗi trong lệnh /promo: {e}")
        await ctx.edit(content=f"❌ Đã xảy ra lỗi khi nhập mã khuyến mãi: `{e}`")
    finally:
        if driver:
            driver.quit()
            print("DEBUG: Trình duyệt đã đóng.")

# --- CHẠY BOT ---
if __name__ == "__main__":
    # Load biến môi trường từ .env nếu chạy cục bộ
    # Railway sẽ tự động cung cấp biến môi trường này
    if not DISCORD_TOKEN and os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
        DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
        print("DEBUG: Đã load DISCORD_TOKEN từ file .env")

    if DISCORD_TOKEN:
        print("DEBUG: Đang khởi động bot...")
        bot.run(DISCORD_TOKEN)
    else:
        print("LỖI KHỞI ĐỘNG: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")
        print("Vui lòng thêm token vào tab 'Variables' trên Railway hoặc file .env (khi chạy cục bộ).")
