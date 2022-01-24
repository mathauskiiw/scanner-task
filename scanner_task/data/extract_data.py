# extract_data.py
# python
import re
import os
from pathlib import Path
from typing import List, Optional, Union
# external
import asyncio
from aiofiles import open as aiopen
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver.chrome.webdriver import WebDriver
# project
from scanner_task.common.utils import adjust_spacing, trim_text
from scanner_task.common.classes import Freelancer, Contact, Address
from scanner_task.common.constants import PERCENTAGE_REGEX
from scanner_task.common.constants import PAYMENT_PRICE_REGEX
from scanner_task.common.constants import CONTACT_INFO_LOOKUP
from scanner_task.common.constants import ADDRESS_INFO_LOOKUP
from scanner_task.common.constants import RESULT_PATH


def page_source_to_file(driver: WebDriver, filename) -> None:
    """
    Gets page source from the driver and saves it to a file in PAGE_SOURCE_PATH
    """
    content = driver.page_source

    with open(filename, 'w') as fp:
        fp.write(content)


def extract_freelancer_data(user_div: Tag) -> Freelancer:
    """
    Processes a div containing data from a single user, gathering user information
    """
    id: str
    name: str
    title: Optional[str]
    img_url: str
    payment_price: float
    payment_rate: str
    earnings: Optional[str] = None
    hours_worked: int = 0
    hourly: int = 0
    fixed: int = 0
    description: str = ''
    job_success_rate: Optional[float] = None
    badge: Optional[str] = None

    # uses freelancer ciphertext as unique id
    if id_div := user_div.find('div', attrs={'data-qa-freelancer-ciphertext': True}):
        id = id_div.get('data-qa-freelancer-ciphertext').lstrip('~')

    if name_div := user_div.find('div', attrs={'class': 'identity-name'}):
        name = trim_text(name_div.text) or 'Anonymous'

    if title_div := user_div.find('p', attrs={'class': 'my-0 freelancer-title'}):
        title = ' '.join(adjust_spacing(title_div.text)) or None

    img_url = user_div.find('img', attrs={'class': 'up-avatar up-avatar-60'}).get('src')

    profile_stats = user_div.find('div', attrs={'class': 'profile-stats mb-10'})

    # payment_price and payment_rate
    if payment_div := profile_stats.find('div', attrs={'data-qa': 'rate'}).find_all('span'):
        if price := re.search(PAYMENT_PRICE_REGEX, payment_div[0].text):
            payment_price = float(price.group())
        payment_rate = payment_div[1].text

    # total_earnings
    if profile_stats and (earnings_div := profile_stats.find('div', attrs={'data-qa': 'earnings'})):
        if text := earnings_div.find('p').text:
            earnings = ' '.join(adjust_spacing(text))

    # hours_worked and job_count
    if popper_div := user_div.find('span', attrs={'id': re.compile(r'popper_*')}).find_all('p'):
        popper_content = []
        for item in popper_div:
            content = adjust_spacing(item.text)
            try:
                value = int(content[0])
            except (IndexError, ValueError):
                # IndexError if content is absent, ValueError if it's 'No'
                value = 0
            popper_content.append(value)
        hourly, fixed, hours_worked = popper_content

    # description
    if desc_div := profile_stats.parent.find('div', attrs={'class': 'up-line-clamp-v2 clamped'}):
        description = desc_div.text
        description = '\n'.join(list(map(lambda x: x.strip(), description.split('\n'))))

    # skills
    skills_div = user_div.find('div', attrs={'class': 'up-skill-wrapper'})
    skills = [trim_text(skill.text) for skill in skills_div.find_all('div')]

    # job success
    if job_success_div := profile_stats.find('span', attrs={'class': 'up-job-success-text'}):
        if percentage := re.search(PERCENTAGE_REGEX, job_success_div.text):
            job_success_rate = float(percentage.group().replace('%', ''))

    # badge
    if badge_div := profile_stats.find('span', attrs={'class': 'status-text d-flex top-rated-badge-status'}):
        badge = trim_text(badge_div.text)

    result = {
        'id': id,
        'name': name,
        'title': title,
        'img_url': img_url,
        'payment_price': payment_price,
        'payment_rate': payment_rate,
        'total_earnings': earnings,
        'hours_worked': hours_worked,
        'job_count': {
            'hourly': hourly,
            'fixed_price': fixed
        },
        'job_success_rate': job_success_rate,
        'description': description,
        'skills': skills,
        'badge': badge
    }
    freelancer = Freelancer(**result)

    return freelancer


def freelancer_page_extract(html_page: str = '') -> List[Freelancer]:
    """
    Compatible with a profile listing html source page like url below

    ref: https://www.upwork.com/ab/profiles/search/?user_pref=1
    """
    if not html_page:
        with open('notes/profile_page1_ref.html', 'r') as fp:
            html_page = fp.read()

    soup: BeautifulSoup = BeautifulSoup(html_page, 'html.parser')
    main_div = soup.find('div', attrs={'class': "up-card my-0 py-0"})
    users = main_div.find_all('div', attrs={'class': "up-card-section up-card-hover"})
    users_data: List[Freelancer] = [extract_freelancer_data(user) for user in users]

    return users_data


def process_contact_info(main_div: Tag) -> Contact:
    """
    Returns the contact info contained on the main div
    """
    result: List[dict] = [{}, {}]

    # saves contact info to result[0], and address info to result[1]
    for idx, lookup in enumerate([CONTACT_INFO_LOOKUP, ADDRESS_INFO_LOOKUP]):
        for key, tag, value in lookup:
            if div_found := main_div.find(tag, attrs={'data-test': value}):
                result[idx][key] = ' '.join(adjust_spacing(div_found.text))
            else:
                result[idx][key] = ''

    addr: Address = Address(**result[1])

    contact: Contact = Contact(**{
        **result[0],
        'address': addr
    })

    return contact


def contact_page_extract(html_page: str = '') -> Contact:
    """
    Compatible with the contact info page displayed on url below

    ref: https://www.upwork.com/freelancers/settings/contactInfo
    """
    if not html_page:
        with open('notes/contact_info.html', 'r') as fp:
            html_page = fp.read()

    soup: BeautifulSoup = BeautifulSoup(html_page, 'html.parser')
    main: Tag = soup.find('main').find('main')

    return process_contact_info(main)


async def parse_file(filepath: str) -> None:
    """
    Routes extract fuction between diferent categories of files and write the results to <RESULT_PATH>
    :param path to a .html file
    """
    async with aiopen(filepath, 'r') as aiof:
        content = await aiof.read()

    result: Union[List[Freelancer], Contact]
    out: str
    if (out := 'contact') in filepath:
        result = contact_page_extract(content)
    elif (out := 'freelancer') in filepath:
        result = freelancer_page_extract(content)

    async with aiopen(os.path.join(RESULT_PATH, out+'.txt'), 'a') as aiof:
        if isinstance(result, list):
            lst = [str(r.json()) for r in result]
            # print(lst)
            await aiof.write('\n'.join(lst))
        else:
            # print(result.json())
            await aiof.write(str(result.json()))
            await aiof.write('\n')


async def parse_all_files(filedir: str) -> List:
    filepaths = Path(filedir).glob('*.html')

    tasks = []
    for fp in filepaths:
        path_str = str(fp.absolute())
        tasks.append(asyncio.ensure_future(parse_file(path_str)))

    parsed_objects = await asyncio.gather(*tasks)

    return parsed_objects
