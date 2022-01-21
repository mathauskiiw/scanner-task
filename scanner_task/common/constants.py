# constants.py
# Paths
CHROME_PATH = '/usr/bin/google-chrome-stable'
CREDENTIALS_FILEPATH = 'scanner_task/resources/user_base.json'
LOG_PATH = 'scanner.log'
LOGIN_URL = 'http://www.upwork.com/ab/account-security/login'
PAGE_SOURCE_PATH = 'scanner_task/resources/page_sources/'
RESULT_PATH = 'scanner_task/resources/outputs/'
WEBDRIVER_PATH = 'scanner_task/resources/chromedriver/chromedriver'

# Regex
PAYMENT_PRICE_REGEX = r'\d+(\.\d+)?'
PERCENTAGE_REGEX = r'(\d+(\.\d+)?%)'

# Lookups
ADDRESS_INFO_LOOKUP = [
    ('street', 'span', 'addressStreet'),
    ('street2', 'span', 'addressStreet2'),
    ('city', 'span', 'addressCity'),
    ('state', 'span', 'addressState'),
    ('zipcode', 'span', 'addressZip'),
    ('country', 'span', 'addressCountry'),
]

CONTACT_INFO_LOOKUP = [
    ('id', 'div', 'userId'),
    ('fullname', 'div', 'userName'),
    ('email', 'div', 'userEmail'),
    ('timezone', 'div', 'timezone'),
    ('phone', 'div', 'phone'),
]
