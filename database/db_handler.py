# database/db_handler.py

import sqlite3
import logging
from datetime import datetime
from config import DB_FILE

logger = logging.getLogger(__name__)

def get_db_connection():
    """Tạo và trả về một kết nối đến DB."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Khởi tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS command_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    command_name TEXT NOT NULL
                )
            """)
            conn.commit()
        logger.info("Cơ sở dữ liệu đã được khởi tạo/kết nối thành công.")
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo DB: {e}", exc_info=True)

def log_command(user_id, user_name, command_name):
    """Ghi lại một lần sử dụng lệnh vào DB."""
    sql = "INSERT INTO command_logs (timestamp, user_id, user_name, command_name) VALUES (?, ?, ?, ?)"
    try:
        with get_db_connection() as conn:
            timestamp = datetime.now().isoformat()
            conn.execute(sql, (timestamp, user_id, user_name, command_name))
            conn.commit()
    except Exception as e:
        logger.error(f"Lỗi khi ghi log lệnh vào DB: {e}", exc_info=True)

def get_command_stats():
    """Lấy thống kê số lần sử dụng của mỗi lệnh."""
    sql = "SELECT command_name, COUNT(*) as count FROM command_logs GROUP BY command_name ORDER BY count DESC"
    try:
        with get_db_connection() as conn:
            stats = conn.execute(sql).fetchall()
            return stats
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê lệnh từ DB: {e}", exc_info=True)
        return []
