# cookie_utils.py
# external
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


def generate_cookie_noise(driver: WebDriver) -> None:
    """
    Access some pages to make the driver fingerprint less suspicious
    """
    driver.get('https://www.google.com/')
    WebDriverWait(driver, 2)
    driver.get('https://www.instagram.com/?hl=en')
    WebDriverWait(driver, 2)
    driver.get('https://www.facebook.com/')
    WebDriverWait(driver, 1)
