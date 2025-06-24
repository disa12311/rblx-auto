# config.py

import os

# --- BIẾN MÔI TRƯỜNG (BẮT BUỘC) ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STATUS_CHANNEL_ID = os.getenv("STATUS_CHANNEL_ID") 

if not DISCORD_TOKEN:
    raise ValueError("Lỗi: Biến môi trường DISCORD_TOKEN chưa được thiết lập.")

if STATUS_CHANNEL_ID:
    try:
        STATUS_CHANNEL_ID = int(STATUS_CHANNEL_ID)
    except ValueError:
        raise ValueError("Lỗi: STATUS_CHANNEL_ID phải là một con số (ID của kênh).")
else:
    print("Cảnh báo: Biến môi trường STATUS_CHANNEL_ID chưa được thiết lập. Bot sẽ không gửi thông báo trạng thái.")


# --- CẤU HÌNH CHUNG ---
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"
LOG_LEVEL = "INFO"
WAIT_TIMEOUT = 15 # Thời gian chờ tối đa cho Selenium (giây)
DB_FILE = "bot_data.db"

# --- CẤU HÌNH TÍNH NĂNG ---
GIVEAWAY_CHECK_INTERVAL_HOURS = 1.0 

# --- CẤU HÌNH SELENIUM ---
SELENIUM_OPTIONS = [
    "--headless", "--no-sandbox", "--disable-dev-shm-usage",
    "--disable-gpu", "window-size=1920,1080"
]

# --- (MỚI) CẤU HÌNH SELECTORS ---
# Tách các bộ chọn ra đây để dễ dàng cập nhật khi website thay đổi.
class Selectors:
    USERNAME_INPUT = '//input[@placeholder="Enter your ROBLOX username"]'
    LINK_ACCOUNT_BUTTON = '//button[contains(text(), "Link Account")]'
    PROMO_PAGE_LINK = '//a[contains(@href, "/promocodes")]'
    PROMO_CODE_INPUT = '//input[@placeholder="Enter a promocode"]'
    PROMO_REDEEM_BUTTON = '//button[contains(text(), "Redeem")]'
    PROMO_RESULT_POPUP = 'swal2-title' # ID
    USER_BALANCE_CONTAINER = "user-balance" # Class Name
    JOIN_GIVEAWAY_PAGE_LINK = '//a[contains(@href, "/giveaways")]'
    JOIN_GIVEAWAY_BUTTON = '//button[contains(text(), "Join Giveaway")]'
