import logging
from utils.app_logger import setup_logger
from selenium_handler.driver_setup import create_driver
from bot.core import RblxBot
from config import DISCORD_TOKEN

# 1. Thiết lập logger trước tiên
logger = setup_logger()

def main():
    driver = None
    try:
        # 2. Khởi tạo Selenium Driver
        driver = create_driver()
        
        # 3. Khởi tạo và chạy bot Discord
        logger.info("Đang khởi động Bot Discord...")
        bot = RblxBot(driver=driver)
        bot.run(DISCORD_TOKEN)
        
    except Exception as e:
        logger.critical(f"Lỗi nghiêm trọng ở main: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Đang đóng Selenium Driver...")
            driver.quit()
        logger.info("Ứng dụng đã đóng.")

if __name__ == "__main__":
    main()
