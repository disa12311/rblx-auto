# Import các thư viện cần thiết
import discord
from discord.commands import Option
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os  # (CẬP NHẬT) Import thư viện 'os' để đọc biến môi trường

# --- CẤU HÌNH ---
# (CẬP NHẬT) Lấy token từ biến môi trường của Railway thay vì ghi thẳng vào code.
# Đây là cách làm bảo mật và đúng chuẩn khi deploy.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"

# --- KHỞI TẠO SELENIUM (CẬP NHẬT CHO MÔI TRƯỜNG SERVER/DOCKER) ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")              # BẮT BUỘC: Chạy ở chế độ không giao diện đồ họa
options.add_argument("--no-sandbox")            # BẮT BUỘC: Cần thiết để chạy Chrome trong môi trường container Docker
options.add_argument("--disable-dev-shm-usage") # BẮT BUỘC: Tránh lỗi tài nguyên và crash trình duyệt
options.add_argument("--disable-gpu")           # Tùy chọn: Tắt GPU vì server không có GPU vật lý
options.add_argument("window-size=1920,1080")   # Tùy chọn: Giả lập kích thước màn hình để tránh layout responsive

# (CẬP NHẬT) Khởi tạo driver. Do Dockerfile đã cài đặt chromedriver vào PATH của hệ thống,
# Selenium sẽ tự động tìm thấy nó mà không cần chúng ta chỉ định đường dẫn.
driver = webdriver.Chrome(options=options)

# --- KHỞI TẠO BOT DISCORD ---
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {bot.user}')
    print('Sẵn sàng nhận lệnh gạch chéo (/). Bot đang chạy trên server.')

# --- CÁC LỆNH GẠCH CHÉO (Không thay đổi logic) ---

# Thay thế hàm start_rblx cũ bằng hàm này
@bot.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
async def start_rblx(
    ctx: discord.ApplicationContext,
    roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
):
    await ctx.defer()
    try:
        # === (CẬP NHẬT) THÊM BƯỚC KIỂM TRA VÀ GHI LOG ===
        # 1. Ghi log để debug: In ra giá trị và kiểu dữ liệu của biến
        print(f"DEBUG: Lệnh /start nhận được. Username: '{roblox_username}', Kiểu: {type(roblox_username)}")

        # 2. Kiểm tra phòng thủ: Đảm bảo biến là một chuỗi hợp lệ và không rỗng
        if not roblox_username or not isinstance(roblox_username, str):
            await ctx.edit(content=f"❌ Lỗi: Tên người dùng Roblox ('{roblox_username}') không hợp lệ. Vui lòng thử lại.")
            return # Dừng hàm nếu không hợp lệ

        # === KẾT THÚC CẬP NHẬT ===

        await ctx.followup.send(f"Đang mở `{WEBSITE_URL}`...")
        driver.get(WEBSITE_URL)
        
        user_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
        )
        
        await ctx.followup.send(f"Đang liên kết tài khoản `{roblox_username}`...")
        
        # === PHƯƠNG ÁN 2: DÙNG JAVASCRIPT ĐỂ NHẬP LIỆU (ỔN ĐỊNH HƠN) ===
        # Thay vì dùng send_keys, chúng ta có thể dùng Javascript để điền giá trị trực tiếp.
        # Cách này thường ổn định hơn và ít gặp lỗi 'invalid argument'.
        driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
        # user_field.send_keys(roblox_username) # Tạm thời vô hiệu hóa dòng này

        link_button = driver.find_element(By.XPATH, '//button[contains(text(), "Link Account")]')
        link_button.click()
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "sidebar-link") and .//span[text()="Earn"]]'))
        )
        
        await ctx.edit(content=f"✅ Đã liên kết tài khoản `{roblox_username}` thành công!")

    except Exception as e:
        # In ra toàn bộ lỗi để dễ dàng chẩn đoán hơn
        print(f"ERROR in start_rblx: {e}")
        await ctx.edit(content=f"❌ Đã xảy ra lỗi trong quá trình thực thi: `{e}`")

@bot.slash_command(name="promo", description="Nhập mã khuyến mãi (promocode) trên rblx.earth.")
async def enter_promo(
    ctx: discord.ApplicationContext,
    code: Option(str, "Mã khuyến mãi bạn muốn nhập.", required=True)
):
    await ctx.defer()
    try:
        await ctx.followup.send("Đang điều hướng đến trang `Promocodes`...")
        promo_page_link = driver.find_element(By.XPATH, '//a[contains(@href, "/promocodes")]')
        promo_page_link.click()
        promo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
        )
        promo_field.send_keys(code)
        redeem_button = driver.find_element(By.XPATH, '//button[contains(text(), "Redeem")]')
        redeem_button.click()
        result_popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'swal2-title'))
        )
        await ctx.edit(content=f"✅ Kết quả nhập mã `{code}`: **{result_popup.text}**")
    except Exception as e:
        await ctx.edit(content=f"❌ Lỗi khi nhập mã khuyến mãi: `{e}`")

@bot.slash_command(name="stop", description="Đóng trình duyệt web mà bot đang điều khiển (chỉ nên dùng khi debug).")
async def stop_browser(ctx: discord.ApplicationContext):
    await ctx.respond("Trên môi trường server, lệnh này sẽ tắt toàn bộ tiến trình. Hãy deploy lại nếu muốn khởi động lại.")
    # Lệnh này sẽ khiến container bị crash, Railway sẽ tự khởi động lại.
    driver.quit()


# --- CHẠY BOT (CẬP NHẬT) ---
# Kiểm tra xem token có được cung cấp không trước khi chạy
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("LỖI: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")
    print("Vui lòng thêm token vào tab 'Variables' trên Railway.")
