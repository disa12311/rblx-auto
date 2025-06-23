import os

# --- BIẾN MÔI TRƯỜG (BẮT BUỘC) ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# (MỚI) Thêm ID của kênh bạn muốn bot gửi thông báo trạng thái (ví dụ: khi tham gia giveaway thành công)
STATUS_CHANNEL_ID = os.getenv("STATUS_CHANNEL_ID") 

if not DISCORD_TOKEN:
    raise ValueError("Lỗi: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")
if not STATUS_CHANNEL_ID:
    print("Cảnh báo: Biến môi trường STATUS_CHANNEL_ID chưa được thiết lập. Bot sẽ không gửi thông báo trạng thái.")
else:
    STATUS_CHANNEL_ID = int(STATUS_CHANNEL_ID)


# --- CẤU HÌNH CHUNG ---
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"
LOG_LEVEL = "INFO"
WAIT_TIMEOUT = 15

# --- (MỚI) CẤU HÌNH TÍNH NĂNG AUTO GIVEAWAY ---
# Khoảng thời gian giữa mỗi lần kiểm tra và tham gia giveaway (tính bằng giờ).
# Ví dụ: 1.5 có nghĩa là 1 giờ 30 phút.
GIVEAWAY_CHECK_INTERVAL_HOURS = 1.0 


# --- CẤU HÌNH SELENIUM ---
SELENIUM_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "window-size=1920,1080"
]
