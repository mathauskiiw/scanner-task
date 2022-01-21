# base.py
# project
from scanner_task.common.utils import get_params_page, retry_n_times
from scanner_task.common.classes import User
from scanner_task.navigation.auth import check_auth_category

# python
import logging
from time import sleep
from typing import List

# external
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scroll_to_bottom(driver):
    """
    scroll to bottom of a webpage
    """
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while not match:
        lastCount = lenOfPage
        sleep(0.5)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True


def next_freelancers_page(driver: WebDriver):
    """
    navigates to next page
    """
    scroll_to_bottom(driver)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div[2]/div/div/div[12]/nav/ul/li[8]/button'))).click()


def previous_freelancers_page(driver: WebDriver):
    """
    navigates to previous page
    """
    scroll_to_bottom(driver)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div[2]/div/div/div[12]/nav/ul/li[1]/button'))).click()


def go_to_freelancers_page(driver: WebDriver, page=None) -> bool:
    """
    navigates from home to reach https://www.upwork.com/ab/profiles/search/?user_pref=1
    """
    if current_page := get_params_page(driver):
        if page and current_page < page:
            try:
                next_freelancers_page(driver)
            except NoSuchElementException:
                logging.info('Reached last page')
                return False

        elif page and current_page > page:
            previous_freelancers_page(driver)

    try:
        # dropdown
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="nav-main"]/div/div/form/div/button[3]'))).click()
        WebDriverWait(driver, 1)

        # select talent
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="nav-main"]/div/div/form/div/ul/li[1]/a'))).click()
        WebDriverWait(driver, 1)

        # click search button
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="nav-main"]/div/div/form/div/button[2]'))).click()
        WebDriverWait(driver, 1)

        WebDriverWait(driver, 3)

        return True
    except TimeoutException as e:
        msg = f"Couldn't reach freelancer's page | {e}"
        logging.error(msg)
        raise Exception(msg)

    retry_n_times(driver, handle_page_errors)

    return True


def go_to_profile_page(driver: WebDriver, user: User) -> bool:
    """
    navigates to profile page :link:
    """
    # Click profile
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="nav-right"]/ul/li[9]/button'))).click()

    # Click 'settings'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="nav-right"]/ul/li[9]/ul/li[3]/ul/li[1]/a'))).click()

    while auth_fn := check_auth_category(driver):
        try:
            auth_fn(driver, user)
        except Exception as e:
            err_msg = f"Couldn't authenticate user: {user.username} using {auth_fn} | error: {e}"
            logging.exception(err_msg)
            raise Exception(err_msg)

    retry_n_times(driver, handle_page_errors)

    return True


def handle_toasters(driver: WebDriver) -> bool:
    """
    Bypass when page shows any toast notification
    """
    # toasters = WebDriverWait(driver, 3).until(EC._find_elements(driver, (By.CLASS_NAME, 'toaster-container')))
    toasters = driver.find_elements_by_class_name('toaster-container')
    for toast_div in toasters:
        buttons = toast_div.find_elements_by_tag_name('button')
        # click all buttons found
        try:
            map(lambda x: x.click(), buttons)
        except ElementNotInteractableException:
            pass
    else:
        # No toasts found, hence no action needed
        return False
    return True


def handle_overwhelmed(driver: WebDriver) -> bool:
    """
    Bypass when page shows "server's overwhelmed" message
    """
    try:
        msg = WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div[2]/div/div/div[2]/p'))).text

        if 'retry' in msg.lower():
            # search for the reload button
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="main"]/div[2]/div[2]/div/div[2]/div/div/div[2]/p/a'))).click()
    except TimeoutException:
        # No server message found, hence no action needed
        return False
    return True


def handle_captcha(driver: WebDriver) -> bool:
    """
    Bypass when eventually some captcha was caught and page needs refreshing
    """
    return False


def handle_page_errors(driver: WebDriver) -> bool:
    """
    Route page handling errors between specified functions
    """
    results: List[bool] = []
    for error_fn in ERROR_HANDLING_FN:
        results.append(error_fn(driver))

    if not any(results):
        # everything seems to be fine with the page...
        return False

    # some action was taken, hopefully it solved the problem...
    return True


def go_to_home_page(driver: WebDriver):
    driver.get('http://www.upwork.com/nx/find-work/best-matches')


# Maps functions used while handling errors
ERROR_HANDLING_FN = [
    handle_toasters,
    handle_overwhelmed,
    handle_captcha,
]
