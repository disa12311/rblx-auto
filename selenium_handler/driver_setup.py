import logging
from selenium import webdriver
from config import SELENIUM_OPTIONS

logger = logging.getLogger(__name__)

def create_driver():
    """
    Tạo và trả về một instance của Selenium WebDriver đã được cấu hình.
    """
    try:
        logger.info("Đang khởi tạo Selenium WebDriver...")
        options = webdriver.ChromeOptions()
        for arg in SELENIUM_OPTIONS:
            options.add_argument(arg)
        
        driver = webdriver.Chrome(options=options)
        logger.info("Selenium WebDriver đã khởi tạo thành công.")
        return driver
    except Exception as e:
        logger.critical(f"Không thể khởi tạo Selenium WebDriver: {e}", exc_info=True)
        raise
