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
    print("Cảnh báo: STATUS_CHANNEL_ID chưa được thiết lập. Bot sẽ không gửi thông báo trạng thái.")

# --- CẤU HÌNH CHUNG ---
WEBSITE_URL = "https://rblx.earth/?referredBy=8404348847"
LOG_LEVEL = "INFO"
WAIT_TIMEOUT = 15
DB_FILE = "bot_data.db"
BOT_COLOR = 0x00A9FF # (MỚI) Màu sắc chủ đạo cho các tin nhắn embed

# --- CẤU HÌNH TÍNH NĂNG ---
GIVEAWAY_CHECK_INTERVAL_HOURS = 1.0 

# --- CẤU HÌNH SELENIUM ---
SELENIUM_OPTIONS = ["--headless", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "window-size=1920,1080"]

# --- (CẬP NHẬT) CẤU HÌNH SELECTORS ---
class Selectors:
    USERNAME_INPUT = '//input[@placeholder="Enter your ROBLOX username"]'
    LINK_ACCOUNT_BUTTON = '//button[contains(text(), "Link Account")]'
    USER_BALANCE_CONTAINER = "user-balance" # Class Name
    
    # Selectors cho trang Promo
    PROMO_PAGE_LINK = '//a[contains(@href, "/promocodes")]'
    PROMO_CODE_INPUT = '//input[@placeholder="Enter a promocode"]'
    PROMO_REDEEM_BUTTON = '//button[contains(text(), "Redeem")]'
    PROMO_RESULT_POPUP = 'swal2-title' # ID
    
    # Selectors cho trang Giveaways
    JOIN_GIVEAWAY_BUTTON = '//button[contains(text(), "Join Giveaway")]'
    
    # (MỚI) Selectors cho trang Rewards
    REWARDS_PAGE_LINK = '//a[contains(@href, "/rewards")]'
    # Giả định có một nút "Claim" cho phần thưởng, cần kiểm tra lại trên web thật
    CLAIM_REWARD_BUTTON = '//button[contains(text(), "Claim")]'
    
    # (MỚI) Selectors cho trang Redeem
    REDEEM_PAGE_LINK = '//a[contains(@href, "/redeem")]'
    REDEEM_AMOUNT_INPUT = '//input[@placeholder="Amount"]'
    REDEEM_USERNAME_INPUT = '//input[@placeholder="Username"]' # Trang redeem có thể yêu cầu nhập lại username
    REDEEM_BUTTON = '//button[text()="Redeem"]'
