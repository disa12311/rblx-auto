import discord
from discord.commands import Option
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service # Cần thiết cho webdriver_manager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import asyncio # Để dùng await asyncio.sleep nếu cần
from webdriver_manager.chrome import ChromeDriverManager # Import webdriver_manager

# --- CẤU HÌNH ---
# Lấy token từ biến môi trường.
# Khi chạy cục bộ, có thể dùng python-dotenv để load từ .env.
# Khi deploy Railway, nó sẽ tự động load từ Railway Variables.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"

# --- CÁC TÙY CHỌN CHO CHROME (GLOBAL) ---
# Hàm này định nghĩa các tùy chọn cho Chrome
# Chúng ta sẽ gọi hàm này mỗi khi khởi tạo driver
def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")              # Chạy không giao diện
    options.add_argument("--no-sandbox")            # Cần thiết cho môi trường container
    options.add_argument("--disable-dev-shm-usage") # Tránh lỗi tài nguyên
    options.add_argument("--disable-gpu")           # Tắt GPU
    options.add_argument("window-size=1920,1080")   # Giả lập kích thước màn hình
    # Thêm một số args khác thường giúp ổn định trên Linux/Docker
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3") # Chỉ hiển thị lỗi nghiêm trọng
    options.add_argument("--disable-logging") # Tắt logging của Chrome
    return options

# --- KHỞI TẠO BOT DISCORD ---
intents = discord.Intents.default()
# intents.message_content = True # Nếu bạn cần đọc nội dung tin nhắn không phải lệnh gạch chéo
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập với tên: {bot.user}')
    print('✅ Sẵn sàng nhận lệnh gạch chéo (/).')

# --- CÁC LỆNH GẠCH CHÉO CỦA BOT ---

@bot.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
async def start_rblx(
    ctx: discord.ApplicationContext,
    roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
):
    await ctx.defer() # Báo cho Discord biết bot đang xử lý

    driver = None # Khởi tạo driver ở đây, sẽ được gán giá trị sau
    try:
        # Debug: In ra giá trị và kiểu dữ liệu của biến
        print(f"DEBUG: Lệnh /start nhận được. Username: '{roblox_username}', Kiểu: {type(roblox_username)}")

        # Kiểm tra tính hợp lệ của username
        if not roblox_username or not isinstance(roblox_username, str):
            await ctx.followup.send(f"❌ Lỗi: Tên người dùng Roblox ('{roblox_username}') không hợp lệ. Vui lòng thử lại.")
            return

        await ctx.followup.send("⏳ Đang khởi tạo trình duyệt và tải trang...")

        # Khởi tạo ChromeDriver sử dụng webdriver_manager
        # Điều này sẽ tự động tải chromedriver tương thích với phiên bản Chrome đã cài
        service_obj = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service_obj, options=get_chrome_options())

        driver.get(WEBSITE_URL)

        # Đợi ô nhập liệu xuất hiện
        user_field = WebDriverWait(driver, 15).until( # Tăng thời gian chờ lên 15s
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )
        await ctx.followup.send(f"➡️ Đã tìm thấy ô nhập liệu. Đang liên kết tài khoản `{roblox_username}`...")

        # Điền tên người dùng bằng JavaScript (ổn định hơn send_keys)
        driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
        
        # Click nút "Link Account"
        link_button = WebDriverWait(driver, 10).until( # Đợi nút có thể click
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Link Account")]'))
        )
        link_button.click()
        
        await ctx.followup.send("⌛ Đã gửi yêu cầu liên kết. Đang đợi trang chính tải...")

        # Đợi cho một phần tử đặc trưng của trang chính xuất hiện sau khi liên kết
        WebDriverWait(driver, 20).until( # Tăng thời gian chờ lên 20s
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "sidebar-link") and .//span[text()="Earn"]]'))
        )
        
        await ctx.edit(content=f"✅ Đã liên kết tài khoản `{roblox_username}` thành công và đang ở trang chính!")

    except Exception as e:
        # Ghi log lỗi đầy đủ vào console của Railway
        print(f"❌ Lỗi trong lệnh /start: {e}")
        await ctx.edit(content=f"❌ Đã xảy ra lỗi khi thực thi lệnh /start: `{e}`")
    finally:
        # Đảm bảo trình duyệt luôn được đóng để giải phóng tài nguyên
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
        print(f"DEBUG: Lệnh /promo nhận được. Code: '{code}'")

        await ctx.followup.send("⏳ Đang khởi tạo trình duyệt và tải trang Promocodes...")
        
        service_obj = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service_obj, options=get_chrome_options())
        
        driver.get(WEBSITE_URL) # Tải lại trang web chính trước

        # Đợi trang tải xong trước khi điều hướng
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )

        # Click vào link dẫn tới trang promocodes
        promo_page_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/promocodes")]'))
        )
        promo_page_link.click()

        await ctx.followup.send(f"➡️ Đang nhập mã `{code}`...")
        
        # Đợi ô nhập mã khuyến mãi xuất hiện
        promo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
        )
        driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
        
        # Click nút Redeem
        redeem_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Redeem")]'))
        )
        redeem_button.click()

        # Đợi pop-up kết quả xuất hiện
        result_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'swal2-title'))
        )
        result_message = result_popup.text
        
        # Đợi và click nút OK trên pop-up (nếu có) để đóng
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
            )
            ok_button.click()
            await asyncio.sleep(0.5) # Chờ một chút để pop-up biến mất
        except:
            print("DEBUG: Không tìm thấy nút 'OK' hoặc pop-up tự đóng.")
            pass # Không tìm thấy nút OK hoặc pop-up tự đóng

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
    # Load biến môi trường từ .env nếu chạy cục bộ (chỉ khi không phải trên Railway)
    # Railway sẽ tự động cung cấp biến môi trường
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
