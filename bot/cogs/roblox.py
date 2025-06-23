# bot/cogs/roblox.py

import logging
import discord
from discord.commands import Option
from discord.ext import commands, tasks
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import WEBSITE_URL, WAIT_TIMEOUT, GIVEAWAY_CHECK_INTERVAL_HOURS, STATUS_CHANNEL_ID

logger = logging.getLogger(__name__)

class RobloxCog(commands.Cog):
    """Cog chứa tất cả các lệnh tương tác với website rblx.earth."""
    
    def __init__(self, bot: commands.Bot, driver: WebDriver):
        self.bot = bot
        self.driver = driver
        # Khởi tạo trạng thái và tác vụ cho Auto Giveaway
        self.auto_giveaway_enabled = False
        self.giveaway_task.start() # Khởi động vòng lặp
        logger.info("RobloxCog đã được tải. Tác vụ Auto Giveaway đã sẵn sàng.")

    def cog_unload(self):
        # Đảm bảo task được hủy khi cog bị unload để tránh lỗi
        self.giveaway_task.cancel()

    async def handle_error(self, ctx: discord.ApplicationContext, error: Exception, command_name: str):
        """Hàm xử lý lỗi tập trung để tránh lặp code và cho trải nghiệm người dùng tốt hơn."""
        logger.error(f"Lỗi trong lệnh /{command_name}: {error}", exc_info=True)
        await ctx.edit(content=(
            f"❌ **Đã có lỗi xảy ra khi thực thi lệnh `/{command_name}`!**\n"
            "Vui lòng thử lại sau. Nếu lỗi vẫn tiếp diễn, có thể website đã thay đổi hoặc bot đang được bảo trì."
        ))

    async def is_logged_in(self):
        """Kiểm tra xem bot đã đăng nhập thành công vào web chưa bằng cách tìm một phần tử chỉ có sau khi đăng nhập."""
        try:
            self.driver.find_element(By.CLASS_NAME, "user-balance")
            return True
        except:
            return False

    # === VÒNG LẶP TỰ ĐỘNG THAM GIA GIVEAWAY ===
    @tasks.loop(hours=GIVEAWAY_CHECK_INTERVAL_HOURS)
    async def giveaway_task(self):
        if not self.auto_giveaway_enabled:
            return
        
        if not await self.is_logged_in():
            logger.warning("Auto Giveaway: Bot chưa đăng nhập, bỏ qua lần tham gia này.")
            return
            
        logger.info("Auto Giveaway: Bắt đầu chu trình tham gia giveaway...")
        try:
            self.driver.get(f"{WEBSITE_URL}giveaways")
            
            join_button_xpath = '//button[contains(text(), "Join Giveaway")]'
            join_button = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, join_button_xpath))
            )
            join_button.click()
            
            success_message = "✅ **Auto Giveaway:** Đã tự động tham gia giveaway thành công!"
            logger.info(success_message)
            
            if STATUS_CHANNEL_ID:
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel:
                    await channel.send(success_message)

        except Exception as e:
            logger.error(f"Auto Giveaway: Đã xảy ra lỗi trong quá trình tham gia: {e}", exc_info=True)
            if STATUS_CHANNEL_ID:
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel:
                    await channel.send(f"❌ **Auto Giveaway:** Gặp lỗi khi cố gắng tham gia giveaway. Chi tiết xem trong log.")

    @giveaway_task.before_loop
    async def before_giveaway_task(self):
        await self.bot.wait_until_ready()

    # === CÁC LỆNH SLASH COMMAND ===
    
    @commands.slash_command(name="auto_giveaway", description="Bật hoặc Tắt tính năng tự động tham gia giveaway.")
    async def auto_giveaway(
        self,
        ctx: discord.ApplicationContext,
        status: Option(str, "Chọn để Bật hoặc Tắt.", choices=["On", "Off"], required=True)
    ):
        await ctx.defer(ephemeral=True)
        if status == "On":
            self.auto_giveaway_enabled = True
            if not self.giveaway_task.is_running():
                self.giveaway_task.start()
            await ctx.edit(content=f"✅ **Đã BẬT** tính năng Auto Giveaway. Bot sẽ tự tham gia mỗi **{GIVEAWAY_CHECK_INTERVAL_HOURS}** giờ.")
            logger.info(f"Auto Giveaway được BẬT bởi người dùng {ctx.author.name}.")
        else:
            self.auto_giveaway_enabled = False
            await ctx.edit(content="❌ **Đã TẮT** tính năng Auto Giveaway.")
            logger.info(f"Auto Giveaway được TẮT bởi người dùng {ctx.author.name}.")

    @commands.slash_command(name="start", description="Mở rblx.earth và liên kết tài khoản Roblox của bạn.")
    async def start(
        self,
        ctx: discord.ApplicationContext,
        roblox_username: Option(str, "Tên người dùng Roblox của bạn để liên kết.", required=True)
    ):
        await ctx.defer()
        try:
            if not roblox_username or not isinstance(roblox_username, str):
                await ctx.edit(content=f"❌ Lỗi: Tên người dùng Roblox không hợp lệ. Vui lòng thử lại.")
                return

            logger.info(f"Executing /start for user: {roblox_username}")
            await ctx.followup.send(f"Đang mở `{WEBSITE_URL}` và chuẩn bị liên kết...")

            self.driver.get(WEBSITE_URL)
            user_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your ROBLOX username"]'))
            )
            
            self.driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
            
            link_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Link Account")]')
            link_button.click()

            WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-balance"))
            )
            await ctx.edit(content=f"✅ **Thành công!** Đã liên kết tài khoản `{roblox_username}`.")

        except Exception as e:
            await self.handle_error(ctx, e, "start")

    @commands.slash_command(name="balance", description="Kiểm tra số dư Robux hiện tại của bạn trên rblx.earth.")
    async def check_balance(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(content="❌ **Lỗi:** Bạn cần phải đăng nhập bằng lệnh `/start` trước khi dùng lệnh này.")
                return

            logger.info(f"Executing /balance for {ctx.author.name}")
            
            balance_element = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-balance"))
            )
            balance_text = balance_element.find_element(By.TAG_NAME, "span").text
            
            await ctx.edit(content=f"💰 **Số dư hiện tại của bạn là:** `{balance_text}`")

        except Exception as e:
            await self.handle_error(ctx, e, "balance")

    @commands.slash_command(name="promo", description="Nhập mã khuyến mãi (promocode) trên rblx.earth.")
    async def enter_promo(
        self,
        ctx: discord.ApplicationContext,
        code: Option(str, "Mã khuyến mãi bạn muốn nhập.", required=True)
    ):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(content="❌ **Lỗi:** Bạn cần phải đăng nhập bằng lệnh `/start` trước khi dùng lệnh này.")
                return

            logger.info(f"Executing /promo with code: {code}")
            await ctx.followup.send("Đang điều hướng đến trang `Promocodes`...")
            
            promo_page_link = self.driver.find_element(By.XPATH, '//a[contains(@href, "/promocodes")]')
            promo_page_link.click()

            promo_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter a promocode"]'))
            )
            self.driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
            
            redeem_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Redeem")]')
            redeem_button.click()

            result_popup = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, 'swal2-title'))
            )
            await ctx.edit(content=f"✅ **Kết quả nhập mã `{code}`:** {result_popup.text}")
            
        except Exception as e:
            await self.handle_error(ctx, e, "promo")

    @commands.slash_command(name="send_to", description="Gửi một tin nhắn đến một kênh hoặc DM cho chính bạn.")
    async def send_to(
        self,
        ctx: discord.ApplicationContext,
        message: Option(str, "Nội dung tin nhắn bạn muốn gửi.", required=True),
        send_dm: Option(str, "Gửi tin nhắn riêng (DM) cho bạn?", choices=["On", "Off"], required=True),
        channel: Option(discord.TextChannel, "Kênh bạn muốn gửi tin nhắn vào.", required=False)
    ):
        await ctx.defer(ephemeral=True)

        if not channel and send_dm == "Off":
            await ctx.edit(content="❌ **Lỗi:** Bạn phải chọn ít nhất một kênh hoặc bật tùy chọn DM.")
            return

        sent_locations = []
        error_locations = []

        if channel:
            try:
                await channel.send(message)
                sent_locations.append(f"kênh {channel.mention}")
            except discord.Forbidden:
                error_locations.append(f"kênh {channel.mention} (thiếu quyền)")
            except Exception as e:
                error_locations.append(f"kênh {channel.mention} (lỗi không xác định)")

        if send_dm == "On":
            try:
                await ctx.author.send(message)
                sent_locations.append("tin nhắn riêng (DM) của bạn")
            except discord.Forbidden:
                error_locations.append("DM của bạn (bạn đã tắt nhận tin nhắn)")
            except Exception as e:
                error_locations.append("DM của bạn (lỗi không xác định)")

        response_parts = []
        if sent_locations:
            response_parts.append(f"✅ Đã gửi tin nhắn thành công đến: {', '.join(sent_locations)}.")
        if error_locations:
            response_parts.append(f"❌ Không thể gửi đến: {', '.join(error_locations)}.")
        
        final_response = "\n".join(response_parts)
        await ctx.edit(content=final_response)

def setup(bot, driver):
    """Hàm thiết lập để bot có thể load Cog này."""
    bot.add_cog(RobloxCog(bot, driver))
