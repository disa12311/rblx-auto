# bot/cogs/rblx.py

import logging
import discord
from discord.commands import Option
from discord.ext import commands, tasks
from discord.ext.commands import is_owner
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

# Import các service, config và DB handlers
from config import *
from selenium_handler.driver_setup import create_driver
from database.db_handler import get_command_stats, log_command
from services import rblx_service
from services.rblx_service import LoginRequiredError, ActionFailedError

logger = logging.getLogger(__name__)

class RblxCog(commands.Cog):
    def __init__(self, bot: commands.Bot, driver: WebDriver):
        self.bot = bot
        self.driver = driver
        self.auto_giveaway_enabled = False
        self.giveaway_task.start()
        logger.info("RobloxCog đã được tải.")

    def cog_unload(self):
        self.giveaway_task.cancel()

    async def handle_error(self, ctx: discord.ApplicationContext, error: Exception, command_name: str):
        logger.error(f"Lỗi trong lệnh /{command_name}: {error}", exc_info=True)
        embed = discord.Embed(title=f"❌ Lỗi khi thực thi `/{command_name}`", description="Đã có lỗi không mong muốn xảy ra. Chi tiết đã được ghi lại trong log.", color=discord.Color.red())
        try:
            await ctx.edit(embed=embed)
        except:
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_application_command(self, ctx: discord.ApplicationContext):
        log_command(ctx.author.id, str(ctx.author), ctx.command.name)
        logger.info(f"Command '{ctx.command.name}' used by '{ctx.author}' (ID: {ctx.author.id})")

    # --- VÒNG LẶP TỰ ĐỘNG ---
    @tasks.loop(hours=GIVEAWAY_CHECK_INTERVAL_HOURS)
    async def giveaway_task(self):
        if not self.auto_giveaway_enabled: return
        try:
            if not rblx_service.get_balance(self.driver): # Dùng get_balance như một cách kiểm tra đăng nhập
                 logger.warning("Auto Giveaway: Bot chưa đăng nhập, bỏ qua."); return
            
            logger.info("Auto Giveaway: Bắt đầu chu trình...")
            rblx_service.join_giveaway(self.driver)
            success_message = "✅ **Auto Giveaway:** Đã tự động tham gia giveaway thành công!"
            logger.info(success_message)
            if STATUS_CHANNEL_ID:
                channel = self.bot.get_channel(STATUS_CHANNEL_ID)
                if channel: await channel.send(embed=discord.Embed(description=success_message, color=discord.Color.green()))
        except (LoginRequiredError, ActionFailedError) as e:
            logger.warning(f"Auto Giveaway: Bỏ qua lần này do: {e}")
        except WebDriverException as e:
            logger.error(f"Auto Giveaway: WebDriver bị lỗi! Đang cố gắng khởi động lại...", exc_info=True)
            try:
                if self.driver: self.driver.quit()
                self.driver = create_driver()
                logger.info("Auto Giveaway: Đã tự động khởi động lại WebDriver.")
            except Exception as restart_e:
                logger.critical(f"Auto Giveaway: KHÔNG THỂ khởi động lại WebDriver. Tác vụ sẽ tạm dừng.", exc_info=True)
                self.auto_giveaway_enabled = False
        except Exception as e:
            logger.error(f"Auto Giveaway: Lỗi không xác định trong quá trình tham gia: {e}", exc_info=True)

    @giveaway_task.before_loop
    async def before_giveaway_task(self):
        await self.bot.wait_until_ready()

    # === LỆNH QUẢN TRỊ ===
    @commands.slash_command(name="restart_selenium", description="(Chủ bot) Khởi động lại trình duyệt Selenium.")
    @is_owner()
    async def restart_selenium(self, ctx):
        await ctx.defer(ephemeral=True)
        try:
            if self.driver: self.driver.quit()
            self.driver = create_driver()
            await ctx.edit(embed=discord.Embed(description="✅ Selenium đã khởi động lại.", color=discord.Color.green()))
        except Exception as e: await self.handle_error(ctx, e, "restart_selenium")
    
    # ... Các lệnh /logs, /stats, và error handler của chúng giữ nguyên như phiên bản trước ...

    # === LỆNH NGƯỜI DÙNG ===
    @commands.slash_command(name="auto_giveaway", description="Bật/Tắt tự động tham gia giveaway.")
    async def auto_giveaway(self, ctx, status: Option(str, "Chọn để Bật hoặc Tắt.", choices=["On", "Off"])):
        # ... Logic lệnh này giữ nguyên như phiên bản trước ...
        pass
        
    @commands.slash_command(name="start", description="Liên kết tài khoản Roblox.")
    async def start(self, ctx, roblox_username: Option(str, "Tên người dùng Roblox.", required=True)):
        await ctx.defer()
        try:
            rblx_service.start_session(self.driver, roblox_username)
            embed = discord.Embed(title="✅ Liên kết thành công!", description=f"Đã liên kết với: **{roblox_username}**.", color=discord.Color.green())
            await ctx.edit(embed=embed)
        except ActionFailedError as e:
            await ctx.edit(embed=discord.Embed(title="❌ Thất bại", description=str(e), color=discord.Color.red()))
        except Exception as e: await self.handle_error(ctx, e, "start")

    @commands.slash_command(name="balance", description="Kiểm tra số dư Robux.")
    async def balance(self, ctx):
        await ctx.defer(ephemeral=True)
        try:
            balance_text = rblx_service.get_balance(self.driver)
            embed = discord.Embed(title="💰 Số dư hiện tại", description=f"Số dư của bạn là: **{balance_text}**", color=BOT_COLOR)
            await ctx.edit(embed=embed)
        except LoginRequiredError as e:
            await ctx.edit(embed=discord.Embed(title="❌ Yêu cầu đăng nhập", description=str(e), color=discord.Color.orange()))
        except Exception as e: await self.handle_error(ctx, e, "balance")

    @commands.slash_command(name="promo", description="Nhập mã khuyến mãi.")
    async def promo(self, ctx, code: Option(str, "Mã khuyến mãi.", required=True)):
        await ctx.defer()
        try:
            # Dùng get_balance như một cách kiểm tra đăng nhập nhanh
            await rblx_service.get_balance(self.driver)
            result_text = rblx_service.enter_promo_code(self.driver, code)
            embed = discord.Embed(title="🎁 Kết quả nhập mã", description=f"Mã `{code}`: **{result_text}**", color=BOT_COLOR)
            await ctx.edit(embed=embed)
        except LoginRequiredError as e:
            await ctx.edit(embed=discord.Embed(title="❌ Yêu cầu đăng nhập", description=str(e), color=discord.Color.orange()))
        except ActionFailedError as e:
            await ctx.edit(embed=discord.Embed(title="❌ Thất bại", description=str(e), color=discord.Color.red()))
        except Exception as e: await self.handle_error(ctx, e, "promo")

    # ... Tương tự, bạn sẽ tái cấu trúc các lệnh /claim_reward, /redeem, /send_to để gọi các hàm từ rblx_service ...

def setup(bot, driver):
    bot.add_cog(RblxCog(bot, driver))
