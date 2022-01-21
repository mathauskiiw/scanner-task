# helpers.py
# python
import os
from random import choice
from string import ascii_lowercase, digits
from typing import Callable, Optional
from urllib.parse import urlparse, parse_qs
# external
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
# project
from scanner_task.common.constants import PAGE_SOURCE_PATH


def trim_text(txt: str) -> str:
    return txt.replace('\t', '').replace('\n', '').strip(' ')


def adjust_spacing(txt: str) -> list:
    """
    Normalize spaces from text that looks like "   Foo             Bar     "
    :param txt input
    :return ["Foo", "Bar"] (Can be joined as needed after)
    """
    arr = list(filter(lambda x: x != '', trim_text(txt).split(' ')))
    return arr


def parse_url_params(driver: WebDriver) -> Optional[dict]:
    """
    Parse params from a driver's current url
    :param WebDriver instance
    :return url params dict
    """
    parsed_url = urlparse(driver.current_url)
    if hasattr(parsed_url, 'query'):
        return parse_qs(parsed_url.query)
    return None


def get_params_page(driver: WebDriver) -> Optional[int]:
    """
    Retrieve page number from url
    :param WebDriver instance
    :return
    """
    if params := parse_url_params(driver):
        if page := params.get('page'):
            return int(page)
    return None


def retry_n_times(driver: WebDriver, fn: Callable, n: int = 3) -> None:
    """
    Try some function n times but stops after its first True return
    :param WebDriver instance
    :param Function to be called
    :param number of times to call
    :raise Exception
    """
    for i in range(n):
        if not fn(driver):
            print("the called function didn't need to take any action")
            return
        else:
            WebDriverWait(2)

    # calling it multiple times, wasn't enough. Dead end
    err = "Couldn't threat the detected error, aborting..."
    raise Exception(err)


def file_suffix(n: int = 4) -> str:
    chars = ascii_lowercase + digits
    lst = [choice(chars) for _ in range(n)]
    return "".join(lst)


def generate_new_filename(basename: str) -> str:
    """
    """
    name, ext = basename.split('.')
    filename = f"{name}_{file_suffix()}.{ext}"
    filepath = os.path.join(PAGE_SOURCE_PATH, filename)

    while os.path.exists(filepath):
        filename = f"{name}_{file_suffix()}.{ext}"
        filepath = os.path.join(PAGE_SOURCE_PATH, filename)

    return filepath
