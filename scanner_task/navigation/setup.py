# setup_webdriver.py

# project
# from scanner_task.common.constants import WEBDRIVER_PATH

# python
import os
from shutil import rmtree

# external
from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver import ChromeOptions
from selenium_stealth import stealth
# from seleniumrequests import Chrome
import undetected_chromedriver as uc

# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.common.proxy import Proxy, ProxyType


def setup_webdriver() -> WebDriver:
    """
    Instantiate the webdriver and add stealth options
    """
    # avoids user staying logged in if not on incognito mode
    if os.path.exists('cookies/'):
        rmtree('cookies/')

    options = uc.ChromeOptions()
    # Those options aren't compatible with undetected_chromedriver
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--disable-blink-features=BlockCredentialedSubresources')
    options.add_argument('--incognito')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-dev-shm-using')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-infobars')
    options.add_argument('--window-size=1700,1100')
    options.add_argument(r'--user-data-dir=./cookies')

    # uncomment when instantiating a local proxy
    # proxy_addr = "http://127.0.0.1:8899"
    # options.add_argument(f"--proxy-server={proxy_addr}")

    # driver = Chrome(options=options, executable_path=WEBDRIVER_PATH)
    driver = uc.Chrome(options=options, browser_executable_path='/usr/bin/google-chrome-stable')

    stealth(
        driver,
        languages=['en-US', 'en'],
        vendor='Google Inc.',
        platform='linux',
        webgl_vendor='Intel Inc.',
        renderer='Intel Iris OpenGL Engine',
        fix_hairline=True,
    )

    return driver
