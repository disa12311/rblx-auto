# bot/core.py

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
        """Tải các cogs từ thư mục cogs."""
        try:
            # Lưu ý tên file đã đổi thành rblx
            self.load_extension("bot.cogs.rblx", driver=self.driver)
            logger.info("Cog 'rblx' đã được tải thành công.")
        except Exception as e:
            logger.critical(f"Lỗi khi tải Cog 'rblx': {e}", exc_info=True)
            
    async def on_ready(self):
        logger.info(f"Bot đã đăng nhập với tên: {self.user} (ID: {self.user.id})")

    # Ghi đè phương thức load_extension để truyền driver vào cog
    def load_extension(self, name: str, *, package: str = None, driver: WebDriver = None):
        super().load_extension(name, package=package)
        # Truyền driver sau khi cog đã được load
        cog = self.get_cog("RblxCog")
        if cog:
            cog.driver = driver
