import os

# --- BIẾN MÔI TRƯỜNG (BẮT BUỘC) ---
# Đọc các thông tin nhạy cảm từ biến môi trường của Railway.
# Điều này áp dụng best practice về bảo mật token.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("Lỗi: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")

# --- CẤU HÌNH CHUNG ---
# Các cài đặt không nhạy cảm có thể được đặt ở đây để dễ dàng thay đổi.
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"
LOG_LEVEL = "INFO" # Có thể đổi thành "DEBUG" để xem log chi tiết hơn
WAIT_TIMEOUT = 15 # Thời gian chờ tối đa cho Selenium (giây)

# --- CẤU HÌNH SELENIUM ---
# Các tùy chọn cho Chrome để chạy ổn định trong môi trường Docker
SELENIUM_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "window-size=1920,1080"
]
