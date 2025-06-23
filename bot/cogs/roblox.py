import logging
from discord.commands import Option
from discord.ext import commands
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import WEBSITE_URL, WAIT_TIMEOUT

logger = logging.getLogger(__name__)

class RobloxCog(commands.Cog):
    """Cog chứa tất cả các lệnh tương tác với website Roblox."""
    
    def __init__(self, bot: commands.Bot, driver: WebDriver):
        self.bot = bot
        self.driver = driver
        logger.info("RobloxCog đã được tải.")

    async def handle_error(self, ctx, error, command_name):
        logger.error(f"Lỗi trong lệnh /{command_name}: {error}", exc_info=True)
        await ctx.edit(content=f"❌ Đã có lỗi xảy ra khi thực thi lệnh `/{command_name}`. Vui lòng thử lại sau.")

    async def is_logged_in(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "user-balance")
            return True
        except:
            return False

    @commands.slash_command(name="start", description="Liên kết tài khoản Roblox của bạn.")
    async def start(self, ctx, roblox_username: Option(str, "Tên người dùng Roblox.", required=True)):
        await ctx.defer()
        try:
            # ... Logic của lệnh /start ...
            self.driver.get(WEBSITE_URL)
            user_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(...)
            # ...
            await ctx.edit(content=f"✅ Đã liên kết tài khoản `{roblox_username}`.")
        except Exception as e:
            await self.handle_error(ctx, e, "start")

    # ... (Các lệnh /promo, /balance tương tự, sử dụng self.driver và self.handle_error) ...

def setup(bot, driver):
    bot.add_cog(RobloxCog(bot, driver))
