# bot/core.py

import logging
import discord
from discord.ext import commands
from selenium.webdriver.remote.webdriver import WebDriver
from bot.cogs.rblx import RblxCog # Import trực tiếp Cog

logger = logging.getLogger(__name__)

class RblxBot(commands.Bot):
    def __init__(self, driver: WebDriver):
        super().__init__(intents=discord.Intents.default())
        # Khởi tạo và thêm Cog thủ công để truyền driver vào
        self.add_cog(RblxCog(self, driver))
        logger.info("Cog 'RblxCog' đã được thêm vào bot.")
            
    async def on_ready(self):
        logger.info(f"Bot đã đăng nhập với tên: {self.user} (ID: {self.user.id})")
