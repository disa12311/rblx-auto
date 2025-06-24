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
from selenium.common.exceptions import WebDriverException, TimeoutException

from config import *
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

    # (TỐI ƯU) Hàm xử lý lỗi giờ sẽ gửi Embed
    async def handle_error(self, ctx: discord.ApplicationContext, error: Exception, command_name: str):
        logger.error(f"Lỗi trong lệnh /{command_name}: {error}", exc_info=True)
        embed = discord.Embed(
            title=f"❌ Lỗi khi thực thi `/{command_name}`",
            description="Đã có lỗi không mong muốn xảy ra. Vui lòng thử lại sau. Nếu lỗi vẫn tiếp diễn, hãy kiểm tra log hoặc liên hệ quản trị viên.",
            color=discord.Color.red()
        )
        # Cố gắng edit phản hồi, nếu không được thì send mới
        try:
            await ctx.edit(embed=embed)
        except:
            await ctx.respond(embed=embed, ephemeral=True)

    async def is_logged_in(self):
        try:
            self.driver.find_element(By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)
            return True
        except:
            return False

    # --- VÒNG LẶP TỰ ĐỘNG ---
    @tasks.loop(hours=GIVEAWAY_CHECK_INTERVAL_HOURS)
    async def giveaway_task(self):
        # ... Logic không thay đổi nhiều ...
        pass # Giữ nguyên logic từ phiên bản trước

    @giveaway_task.before_loop
    async def before_giveaway_task(self):
        await self.bot.wait_until_ready()

    # === CÁC LỆNH NGƯỜI DÙNG & TỰ ĐỘNG HÓA ===

    @commands.slash_command(name="start", description="Liên kết tài khoản Roblox của bạn.")
    async def start(self, ctx, roblox_username: Option(str, "Tên người dùng Roblox.", required=True)):
        await ctx.defer()
        try:
            self.driver.get(WEBSITE_URL)
            user_field = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.USERNAME_INPUT)))
            self.driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
            self.driver.find_element(By.XPATH, Selectors.LINK_ACCOUNT_BUTTON).click()
            WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)))
            
            embed = discord.Embed(title="✅ Liên kết thành công!", description=f"Bot đã liên kết thành công với tài khoản Roblox: **{roblox_username}**.", color=discord.Color.green())
            await ctx.edit(embed=embed)
        except Exception as e: await self.handle_error(ctx, e, "start")

    @commands.slash_command(name="balance", description="Kiểm tra số dư Robux hiện tại.")
    async def balance(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        try:
            if not await self.is_logged_in():
                await ctx.edit(embed=discord.Embed(title="❌ Chưa đăng nhập", description="Bạn cần dùng lệnh `/start` trước.", color=discord.Color.orange()))
                return
            balance_element = self.driver.find_element(By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)
            balance_text = balance_element.find_element(By.TAG_NAME, "span").text
            embed = discord.Embed(title="💰 Số dư hiện tại", description=f"Số dư của bạn là: **{balance_text}**", color=BOT_COLOR)
            await ctx.edit(embed=embed)
        except Exception as e: await self.handle_error(ctx, e, "balance")

    # (MỚI) LỆNH NHẬN THƯỞNG
    @commands.slash_command(name="claim_reward", description="Tự động nhận phần thưởng hàng ngày (nếu có).")
    async def claim_reward(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(embed=discord.Embed(title="❌ Chưa đăng nhập", description="Bạn cần dùng lệnh `/start` trước.", color=discord.Color.orange()))
                return

            logger.info(f"Executing /claim_reward for {ctx.author.name}")
            self.driver.get(f"{WEBSITE_URL}rewards")
            
            # Cố gắng tìm và nhấn nút claim
            claim_button = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, Selectors.CLAIM_REWARD_BUTTON)))
            claim_button.click()
            
            # Đợi và kiểm tra kết quả (giả định có popup)
            result_popup = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
            
            embed = discord.Embed(title="🎁 Nhận thưởng", description=f"Kết quả: **{result_popup.text}**", color=BOT_COLOR)
            await ctx.edit(embed=embed)

        except TimeoutException:
            logger.warning("Không tìm thấy nút 'Claim' hoặc không có popup kết quả. Có thể đã nhận hoặc không có thưởng.")
            embed = discord.Embed(title="🎁 Nhận thưởng", description="Không tìm thấy nút nhận thưởng. Có thể bạn đã nhận rồi hoặc không có phần thưởng nào.", color=discord.Color.orange())
            await ctx.edit(embed=embed)
        except Exception as e:
            await self.handle_error(ctx, e, "claim_reward")

    # (MỚI) LỆNH RÚT ROBUX
    @commands.slash_command(name="redeem", description="Tự động rút Robux về tài khoản của bạn.")
    async def redeem(self, ctx, amount: Option(int, "Số lượng Robux muốn rút.", min_value=1)):
        await ctx.defer()
        try:
            if not await self.is_logged_in():
                await ctx.edit(embed=discord.Embed(title="❌ Chưa đăng nhập", description="Bạn cần dùng lệnh `/start` trước.", color=discord.Color.orange()))
                return

            logger.info(f"Executing /redeem for {ctx.author.name} with amount {amount}")
            self.driver.get(f"{WEBSITE_URL}redeem")

            amount_input = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.REDEEM_AMOUNT_INPUT)))
            self.driver.execute_script("arguments[0].value = arguments[1];", amount_input, amount)
            
            # Giả sử trang redeem tự điền username đã liên kết, nếu không, phải tìm và điền thêm
            redeem_button = self.driver.find_element(By.XPATH, Selectors.REDEEM_BUTTON)
            redeem_button.click()

            result_popup = WebDriverWait(self.driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
            embed = discord.Embed(title="💸 Rút Robux", description=f"Kết quả rút **{amount} R$**: **{result_popup.text}**", color=discord.Color.green())
            await ctx.edit(embed=embed)

        except Exception as e:
            await self.handle_error(ctx, e, "redeem")

    # (CẢI TIẾN) LỆNH SEND_TO
    @commands.slash_command(name="send_to", description="Gửi một tin nhắn nhúng (embed) đến kênh hoặc DM.")
    async def send_to(
        self,
        ctx: discord.ApplicationContext,
        title: Option(str, "Tiêu đề của tin nhắn embed.", required=True),
        description: Option(str, "Nội dung/mô tả của tin nhắn embed.", required=True),
        send_dm: Option(str, "Gửi tin nhắn riêng (DM) cho bạn?", choices=["On", "Off"]),
        channel: Option(discord.TextChannel, "Kênh muốn gửi tin nhắn vào.", required=False)
    ):
        await ctx.defer(ephemeral=True)
        if not channel and send_dm == "Off":
            await ctx.edit(content="❌ Bạn phải chọn ít nhất một nơi để gửi.")
            return

        # Tạo embed
        embed_to_send = discord.Embed(title=title, description=description, color=BOT_COLOR)
        embed_to_send.set_footer(text=f"Tin nhắn được gửi bởi {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        sent_locations, error_locations = [], []
        if channel:
            try:
                await channel.send(embed=embed_to_send); sent_locations.append(f"kênh {channel.mention}")
            except: error_locations.append(f"kênh {channel.mention}")
        if send_dm == "On":
            try:
                await ctx.author.send(embed=embed_to_send); sent_locations.append("DM của bạn")
            except: error_locations.append("DM của bạn (có thể bạn đã chặn)")
        
        response_parts = []
        if sent_locations: response_parts.append(f"✅ Đã gửi thành công đến: {', '.join(sent_locations)}.")
        if error_locations: response_parts.append(f"❌ Không thể gửi đến: {', '.join(error_locations)}.")
        await ctx.edit(content="\n".join(response_parts))

    # ... (Các lệnh quản trị và lệnh auto_giveaway giữ nguyên như phiên bản trước) ...


def setup(bot, driver):
    """Hàm thiết lập để bot có thể load Cog này."""
    bot.add_cog(RblxCog(bot, driver))
