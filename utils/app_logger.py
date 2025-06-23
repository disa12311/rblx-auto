import logging
import sys
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL

def setup_logger():
    """
    Thiết lập hệ thống logging tập trung cho toàn bộ ứng dụng.
    Ghi log ra cả console và file 'bot.log'.
    """
    # Lấy logger gốc
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Định dạng cho log message
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Handler để ghi log ra console (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)

    # Handler để ghi log ra file, với chức năng xoay vòng file khi đạt 2MB
    file_handler = RotatingFileHandler('bot.log', maxBytes=2*1024*1024, backupCount=5)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logging.info("Logger đã được thiết lập thành công.")
    return logger
