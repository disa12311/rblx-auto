# services/rblx_service.py

import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import WEBSITE_URL, WAIT_TIMEOUT, Selectors

logger = logging.getLogger(__name__)

# --- Các lớp Lỗi tùy chỉnh để giao tiếp giữa Service và Cog ---
class RblxServiceError(Exception):
    """Lỗi cơ bản cho các vấn đề liên quan đến rblx_service."""
    pass

class LoginRequiredError(RblxServiceError):
    """Lỗi xảy ra khi thực hiện hành động yêu cầu đăng nhập trước."""
    pass

class ActionFailedError(RblxServiceError):
    """Lỗi khi một hành động trên web không mang lại kết quả mong muốn."""
    pass


# === CÁC HÀM TƯƠNG TÁC VỚI WEBSITE ===

def start_session(driver: WebDriver, roblox_username: str):
    """Thực hiện quy trình đăng nhập/liên kết tài khoản.
    Ném ra ActionFailedError nếu thất bại.
    """
    try:
        logger.info(f"Đang bắt đầu phiên cho người dùng: {roblox_username}")
        driver.get(WEBSITE_URL)
        user_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, Selectors.USERNAME_INPUT))
        )
        driver.execute_script("arguments[0].value = arguments[1];", user_field, roblox_username)
        driver.find_element(By.XPATH, Selectors.LINK_ACCOUNT_BUTTON).click()
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER))
        )
        logger.info(f"Liên kết thành công cho {roblox_username}.")
    except TimeoutException:
        logger.error(f"Timeout khi cố gắng liên kết tài khoản {roblox_username}.")
        raise ActionFailedError("Không thể liên kết tài khoản. Có thể tên người dùng sai, website đang chậm hoặc đã thay đổi cấu trúc.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi bắt đầu phiên: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")

def get_balance(driver: WebDriver) -> str:
    """Lấy số dư hiện tại. Ném ra LoginRequiredError nếu chưa đăng nhập."""
    try:
        balance_element = driver.find_element(By.CLASS_NAME, Selectors.USER_BALANCE_CONTAINER)
        return balance_element.find_element(By.TAG_NAME, "span").text
    except NoSuchElementException:
        logger.warning("Không tìm thấy phần tử số dư. Người dùng có thể chưa đăng nhập.")
        raise LoginRequiredError("Không tìm thấy thông tin người dùng. Vui lòng dùng `/start` trước.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi lấy số dư: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")

def enter_promo_code(driver: WebDriver, code: str) -> str:
    """Điều hướng, nhập và nhận kết quả từ promo code."""
    try:
        driver.get(f"{WEBSITE_URL}promocodes")
        promo_field = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.PROMO_CODE_INPUT)))
        driver.execute_script("arguments[0].value = arguments[1];", promo_field, code)
        driver.find_element(By.XPATH, Selectors.PROMO_REDEEM_BUTTON).click()
        result_popup = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
        return result_popup.text
    except TimeoutException:
        raise ActionFailedError("Không tìm thấy ô nhập liệu hoặc popup kết quả. Website có thể đã thay đổi.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi nhập promo code: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")

def claim_reward(driver: WebDriver) -> str:
    """Cố gắng nhận phần thưởng hàng ngày."""
    try:
        driver.get(f"{WEBSITE_URL}rewards")
        claim_button = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, Selectors.CLAIM_REWARD_BUTTON)))
        claim_button.click()
        result_popup = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
        return result_popup.text
    except TimeoutException:
        raise ActionFailedError("Không tìm thấy nút nhận thưởng. Có thể bạn đã nhận rồi hoặc không có phần thưởng nào.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi nhận thưởng: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")

def redeem_robux(driver: WebDriver, amount: int) -> str:
    """Thực hiện quy trình rút Robux."""
    try:
        driver.get(f"{WEBSITE_URL}redeem")
        amount_input = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, Selectors.REDEEM_AMOUNT_INPUT)))
        driver.execute_script("arguments[0].value = arguments[1];", amount_input, amount)
        driver.find_element(By.XPATH, Selectors.REDEEM_BUTTON).click()
        result_popup = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Selectors.PROMO_RESULT_POPUP)))
        return result_popup.text
    except TimeoutException:
        raise ActionFailedError("Không thể hoàn thành thao tác rút tiền. Website có thể đã thay đổi.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi rút Robux: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")

def join_giveaway(driver: WebDriver):
    """Tham gia sự kiện giveaway."""
    try:
        driver.get(f"{WEBSITE_URL}giveaways")
        join_button = WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, Selectors.JOIN_GIVEAWAY_BUTTON)))
        join_button.click()
        logger.info("Đã nhấn nút tham gia giveaway thành công.")
    except TimeoutException:
        logger.warning("Không tìm thấy nút 'Join Giveaway'. Có thể đã tham gia hoặc không có sự kiện.")
        raise ActionFailedError("Không tìm thấy nút tham gia. Có thể bạn đã tham gia rồi.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi tham gia giveaway: {e}", exc_info=True)
        raise RblxServiceError(f"Đã xảy ra lỗi không mong muốn: {e}")
