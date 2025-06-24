# bot/core.py

import logging
import discord
from discord.ext import commands
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

class RblxBot(commands.Bot):
    def __init__(self, driver: WebDriver):
        # Truyền driver vào đây không phải là cách làm đúng khi dùng extension.
        # Driver sẽ được quản lý và truyền vào khi load cog.
        super().__init__(intents=discord.Intents.default())
        # Lưu driver vào bot để có thể truy cập từ extension
        self.driver = driver
        self.load_extension("bot.cogs.rblx")
            
    async def on_ready(self):
        logger.info(f"Bot đã đăng nhập với tên: {self.user} (ID: {self.user.id})")
