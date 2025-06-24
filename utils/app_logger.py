# utils/app_logger.py

import logging
import sys
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL

def setup_logger():
    """Thiết lập hệ thống logging tập trung."""
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logging.info("Logger đã được thiết lập.")
    return logger
