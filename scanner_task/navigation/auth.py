# auth.py
# project
from scanner_task.common.constants import LOGIN_URL
from scanner_task.common.classes import User
from time import sleep

# python
import logging
from typing import Callable, Optional

# external
import pyotp
from retrying import retry
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def authenticate(driver: WebDriver, user: User) -> bool:
    """
    Authenticate user given the credentials
    """
    sleep(2)
    driver.get(LOGIN_URL)

    if not check_is_login_page(driver):
        # already authenticated!
        return True

    # try:
    #     login_field = driver.find_element_by_id('login_username')
    # except NoSuchElementException:
    #     driver.refresh()
    #     try:
    #         login_field = driver.find_element_by_id('login_username')
    #     except NoSuchElementException:
    #         return False
    # login_field.send_keys(user.username)
    # driver.find_element_by_id('login_password_continue').click()
    # login_field.send_keys(Keys.RETURN)
    # WebDriverWait(driver, 15).until(EC.element_to_be_clickable(By.ID, 'login_password')).send_keys(user['password'])
    # sleep(2)
    # pwd_field = driver.find_element_by_id('login_password')
    # pwd_field.send_keys(user.password)
    # driver.find_element_by_id('login_control_continue').click()
    # # pwd_field.send_keys(Keys.RETURN)
    try:
        # username
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'login_username'))).send_keys(user.username)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'login_password_continue'))).click()

        # password
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'login_password'))).send_keys(user.password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'login_control_continue'))).click()

        WebDriverWait(driver, 3)

    except TimeoutException as e:
        err_msg = f"Couldn't authenticate user: {user.username} | Login page | error: {e}"
        logging.exception(err_msg)
        raise Exception(err_msg)

    if not check_is_login_page(driver):
        return True

    # while page can be resolved by one of the authentication methods, keep trying
    while auth_fn := check_auth_category(driver):
        try:
            auth_fn(driver, user)
        except Exception as e:
            err_msg = f"Couldn't authenticate user: {user.username} using {auth_fn} | error: {e}"
            logging.exception(err_msg)
            raise Exception(err_msg)

    return True


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_delay=30000)
def fill_totp(driver: WebDriver, user: User) -> None:
    """
    Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds,
    then 10 seconds afterwards, for a maximum of 30 seconds.
    """
    try:
        totp_field = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, 'deviceAuthOtp_otp')))
        if key := user.authenticator_key:
            totp = pyotp.TOTP(key.replace(' ', ''))
            totp_field.send_keys(totp.now())
            totp_field.send_keys(Keys.RETURN)
        else:
            err_msg = f"No authentication key available for user: {user.username}"
            logging.exception(err_msg)
            raise Exception(err_msg)

    except TimeoutException:
        if totp_error := WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'otp-message'))):
            # todo test agains child text
            # The code you’ve entered is invalid. Please try again.
            if 'invalid' in totp_error.text.lower():
                raise Exception("Retry!")


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_delay=30000)
def fill_secret_answer(driver: WebDriver, user: User) -> None:
    """
    Wait 2^x * 1000 milliseconds between each retry, up to 10 seconds,
    then 10 seconds afterwards, for a maximum of 30 seconds.
    """
    try:
        sa_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'deviceAuth_answer')))
        if answer := user.secret_answer:
            sa_field.send_keys(answer)
            sa_field.send_keys(Keys.RETURN)
        else:
            err_msg = f"No secret answer available for user: {user.username}"
            logging.exception(err_msg)
            raise Exception(err_msg)
    except TimeoutException:
        if sa_error := WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'answer-message'))):
            if 'incorrect' in sa_error.text.lower():
                raise Exception("Retry!")


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_delay=30000)
def re_enter_password(driver: WebDriver, user: User) -> None:
    try:
        pwd_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'sensitiveZone_password')))
        if pwd := user.password:
            pwd_field.send_keys(pwd)
            pwd_field.send_keys(Keys.RETURN)
        else:
            err_msg = f"No password available for user: {user.username}"
            logging.exception(err_msg)
            raise Exception(err_msg)
    except TimeoutException:
        if pwd_error := WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password-message'))):
            if 'invalid' in pwd_error.text.lower():
                raise Exception("Retry!")


def check_auth_category(driver: WebDriver) -> Optional[Callable]:
    """
    Return function to navigate through the detected auth category (totp, secret_answer, etc)
    """
    for auth_elem_id, auth_fn in AUTH_METHOD_MAPPING.items():
        try:
            if WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, auth_elem_id))):
                return auth_fn
        except TimeoutException:
            # The tested auth method don't need to be used
            pass
    return None


def check_is_login_page(driver: WebDriver) -> bool:
    # if driver.title == 'Upwork':
    #     return True
    # return False
    try:
        WebDriverWait(driver, 2).until(EC.url_contains('/login'))
        return True
    except TimeoutException:
        return False


# Auth function lookup - needs to be defined in this file to avoid circular dependency
AUTH_METHOD_MAPPING = {
    'deviceAuthOtp_otp': fill_totp,
    'deviceAuth_answer': fill_secret_answer,
    'sensitiveZone_password': re_enter_password
}
