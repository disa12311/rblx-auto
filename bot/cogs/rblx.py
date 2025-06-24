# bot/cogs/rblx.py

import logging
import discord
from discord.commands import Option
from discord.ext import commands, tasks
from discord.ext.commands import is_owner
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from config import WEBSITE_URL, WAIT_TIMEOUT, GIVEAWAY_CHECK_INTERVAL_HOURS, STATUS_CHANNEL_ID, Selectors
from selenium_handler.driver_setup import create_driver
from database.db_handler import get_command_stats

logger = logging.getLogger(__name__)

class RblxCog(commands.Cog):
    """Cog chứa tất cả các lệnh tương tác với website rblx.earth."""
    
    def __init__(self, bot: commands.Bot, driver: WebDriver):
        self.bot = bot
        self.driver = driver
        self.auto_giveaway_enabled = False
        self.giveaway_task.start()
        logger.info("RobloxCog đã được tải. Tác vụ Auto Giveaway đã sẵn sàng.")

    def cog_unload(self):
        self.giveaway_task.cancel()

    async def handle_error(self, ctx: discord.ApplicationContext, error: Exception, command_name: str):
        logger.error(f"Lỗi trong lệnh /{command_name}: {error}", exc_info=True)
        await ctx.edit(content=f"❌ Đã có lỗi khi thực thi `/{command_name}`. Vui lòng thử lại sau.")

    async def is_logged_in(self):
        try:
            self.driver.find_element(By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)
            return True
        except:
            return False

    # --- VÒNG LẶP TỰ ĐỘNG ---
    @tasks.loop(hours=GIVEAWAY_CHECK_INTERVAL_HOURS)
    async def giveaway_task(self):
        if not self.auto_giveaway_enabled: return
        if not await self.is_logged_in():
            logger.warning("Auto Giveaway: Bot chưa đăng nhập, bỏ qua.")
            return
            
        logger.info("Auto Giveaway: Bắt đầu chu trình...")
        try:
            self.driver.get(f"{WEBSITE_URL}giveaways")
            join_button = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, Selectors.JOIN_GIVEAWAY_BUTTON))
            )
            join_button.click()
            success_message = "✅ **Auto Giveaway:** Đã tự động tham gia giveaway thành công!"
            logger.info(success_message)
            if STATUS_CHANNEL_ID:
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel: await channel.send(success_message)
        except WebDriverException as e:
            logger.error(f"Auto Giveaway: WebDriver bị lỗi! Đang cố gắng khởi động lại... Lỗi: {e}")
            try:
                if self.driver: self.driver.quit()
                self.driver = create_driver()
                logger.info("Auto Giveaway: Đã tự động khởi động lại WebDriver.")
            except Exception as restart_e:
                logger.critical(f"Auto Giveaway: KHÔNG THỂ khởi động lại WebDriver. Tác vụ sẽ tạm dừng. Lỗi: {restart_e}")
                self.auto_giveaway_enabled = False
        except Exception as e:
            logger.error(f"Auto Giveaway: Lỗi trong quá trình tham gia: {e}", exc_info=True)
            if STATUS_CHANNEL_ID:
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel: await channel.send(f"❌ **Auto Giveaway:** Gặp lỗi. Chi tiết xem trong log.")

    @giveaway_task.before_loop
    async def before_giveaway_task(self):
        await self.bot.wait_until_ready()

    # --- CÁC LỆNH QUẢN TRỊ ---
    @commands.slash_command(name="restart_selenium", description="(Chủ bot) Khởi động lại trình duyệt Selenium.")
    @is_owner()
    async def restart_selenium(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        logger.info(f"Yêu cầu khởi động lại Selenium từ {ctx.author.name}...")
        try:
            if self.driver: self.driver.quit()
            self.driver = create_driver()
            await ctx.edit(content="✅ Trình duyệt Selenium đã được khởi động lại thành công.")
        except Exception as e:
            await self.handle_error(ctx, e, "restart_selenium")

    @commands.slash_command(name="logs", description="(Chủ bot) Lấy các dòng log cuối cùng từ file.")
    @is_owner()
    async def get_logs(self, ctx, lines: Option(int, "Số dòng log.", min_value=1, max_value=100, default=20)):
        await ctx.defer(ephemeral=True)
        try:
            with open("bot.log", "r", encoding="utf-8") as f:
                log_content = "".join(f.readlines()[-lines:])
            if not log_content:
                await ctx.edit(content="File log trống.")
                return
            if len(log_content) > 1900:
                with open("log.txt", "w", encoding="utf-8") as f: f.write(log_content)
                await ctx.edit(content=f"Log quá dài, gửi dạng file.", file=discord.File("log.txt"))
            else:
                await ctx.edit(content=f"📄 **{lines} dòng log cuối cùng:**\n```log\n{log_content}\n```")
        except Exception as e: await self.handle_error(ctx, e, "logs")

    @commands.slash_command(name="stats", description="(Chủ bot) Xem thống kê sử dụng lệnh.")
    @is_owner()
    async def stats(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        try:
            stats_data = get_command_stats()
            if not stats_data:
                await ctx.edit(content="Chưa có dữ liệu thống kê nào.")
                return
            
            embed = discord.Embed(title="📊 Thống kê sử dụng lệnh", color=discord.Color.blue())
            description = ""
            for row in stats_data:
                description += f"**/{row['command_name']}**: {row['count']} lần\n"
            embed.description = description
            await ctx.edit(embed=embed)
        except Exception as e: await self.handle_error(ctx, e, "stats")
        
    @restart_selenium.error
    @get_logs.error
    @stats.error
    async def on_owner_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("❌ Lệnh này chỉ dành cho chủ sở hữu của bot.", ephemeral=True)

    # --- CÁC LỆNH NGƯỜI DÙNG ---
    @commands.slash_command(name="auto_giveaway", description="Bật/Tắt tính năng tự động tham gia giveaway.")
    async def auto_giveaway(self, ctx, status: Option(str, "Chọn để Bật hoặc Tắt.", choices=["On", "Off"])):
        await ctx.defer(ephemeral=True)
        if status == "On":
            self.auto_giveaway_enabled = True
            if not self.giveaway_task.is_running(): self.giveaway_task.start()
            await ctx.edit(content=f"✅ **Đã BẬT** Auto Giveaway. Bot sẽ kiểm tra mỗi **{GIVEAWAY_CHECK_INTERVAL_HOURS}** giờ.")
        else:
            self.auto_giveaway_enabled = False
            await ctx.edit(content="❌ **Đã TẮT** Auto Giveaway.")

    @commands.slash_command(name="start", description="Liên kết tài khoản Roblox của bạn.")
    async def start(self, ctx, roblox_username: Option(str, "Tên người dùng Roblox.", required=True)):
        await ctx.defer()
        try:
            self.driver.get(WEBSITE_URL)
            user_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.USERNAME_INPUT)))
            self.driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
            self.driver.find_element(By.XPATH, Selectors.LINK_ACCOUNT_BUTTON).click()
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)))
            await ctx.edit(content=f"✅ **Thành công!** Đã liên kết tài khoản `{roblox_username}`.")
        except Exception as e: await self.handle_error(ctx, e, "start")

    @commands.slash_command(name="balance", description="Kiểm tra số dư Robux hiện tại.")
    async def balance(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(content="❌ Bạn cần `/start` trước khi dùng lệnh này.")
                return
            balance_element = self.driver.find_element(By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)
            balance_text = balance_element.find_element(By.TAG_NAME, "span").text
            await ctx.edit(content=f"💰 **Số dư của bạn:** `{balance_text}`")
        except Exception as e: await self.handle_error(ctx, e, "balance")

    @commands.slash_command(name="promo", description="Nhập mã khuyến mãi.")
    async def promo(self, ctx, code: Option(str, "Mã khuyến mãi.", required=True)):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(content="❌ Bạn cần `/start` trước khi dùng lệnh này.")
                return
            self.driver.get(f"{WEBSITE_URL}promocodes")
            promo_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.PROMO_CODE_INPUT)))
            self.driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
            self.driver.find_element(By.XPATH, Selectors.PROMO_REDEEM_BUTTON).click()
            result_popup = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
            await ctx.edit(content=f"✅ **Kết quả nhập mã `{code}`:** {result_popup.text}")
        except Exception as e: await self.handle_error(ctx, e, "promo")

    @commands.slash_command(name="send_to", description="Gửi tin nhắn đến kênh hoặc DM.")
    async def send_to(self, ctx, message: Option(str, "Nội dung tin nhắn.", required=True), send_dm: Option(str, "Gửi DM cho bạn?", choices=["On", "Off"]), channel: Option(discord.TextChannel, "Kênh muốn gửi.", required=False)):
        await ctx.defer(ephemeral=True)
        if not channel and send_dm == "Off":
            await ctx.edit(content="❌ Bạn phải chọn ít nhất một nơi để gửi.")
            return
        sent_locations, error_locations = [], []
        if channel:
            try:
                await channel.send(message); sent_locations.append(f"kênh {channel.mention}")
            except: error_locations.append(f"kênh {channel.mention}")
        if send_dm == "On":
            try:
                await ctx.author.send(message); sent_locations.append("DM của bạn")
            except: error_locations.append("DM của bạn (có thể bạn đã chặn)")
        
        response_parts = []
        if sent_locations: response_parts.append(f"✅ Đã gửi thành công đến: {', '.join(sent_locations)}.")
        if error_locations: response_parts.append(f"❌ Không thể gửi đến: {', '.join(error_locations)}.")
        await ctx.edit(content="\n".join(response_parts))

def setup(bot, driver):
    bot.add_cog(RblxCog(bot, driver))
