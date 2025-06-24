# main.py

import logging
from utils.app_logger import setup_logger
from database.db_handler import init_db
from selenium_handler.driver_setup import create_driver
from bot.core import RblxBot
from config import DISCORD_TOKEN

# 1. Thiết lập logger là việc đầu tiên
logger = setup_logger()

def main():
    driver = None
    try:
        # 2. Khởi tạo cơ sở dữ liệu
        init_db()

        # 3. Khởi tạo Selenium Driver
        driver = create_driver()
        
        # 4. Khởi tạo và chạy bot Discord, truyền driver vào
        logger.info("Đang khởi động Bot Discord...")
        bot = RblxBot(driver=driver)
        bot.run(DISCORD_TOKEN)
        
    except Exception as e:
        logger.critical(f"Lỗi nghiêm trọng ở tầng main, ứng dụng dừng lại: {e}", exc_info=True)
    finally:
        # 5. Đảm bảo driver luôn được đóng khi ứng dụng kết thúc
        if driver:
            logger.info("Đang đóng Selenium Driver...")
            driver.quit()
        logger.info("Ứng dụng đã đóng.")

if __name__ == "__main__":
    main()
