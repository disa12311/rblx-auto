import logging
import discord
from discord.ext import commands
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

class RblxBot(commands.Bot):
    def __init__(self, driver: WebDriver):
        super().__init__(intents=discord.Intents.default())
        self.driver = driver
        self.load_cogs()

    def load_cogs(self):
        # Tự động load tất cả các file trong thư mục cogs
        # Ở đây chúng ta load thủ công để truyền driver vào
        try:
            from .cogs.roblox import setup as setup_roblox
            setup_roblox(self, self.driver)
            logger.info("Tất cả các Cogs đã được tải thành công.")
        except Exception as e:
            logger.critical(f"Lỗi khi tải Cogs: {e}", exc_info=True)
            
    async def on_ready(self):
        logger.info(f"Bot đã đăng nhập với tên: {self.user}")
        logger.info(f"ID của Bot: {self.user.id}")
