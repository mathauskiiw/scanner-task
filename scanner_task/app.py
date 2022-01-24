
# app.py
# python
import logging
from time import sleep
# external
import asyncio
# project
from scanner_task.bypassing.cursor_movement import start_cursor_thread, kill_task
from scanner_task.common.utils import generate_new_filename
from scanner_task.common.constants import PAGE_SOURCE_PATH
from scanner_task.data.data_loader import load_credentials
from scanner_task.data.extract_data import page_source_to_file, parse_all_files
from scanner_task.navigation.auth import authenticate
from scanner_task.navigation.setup import setup_webdriver
from scanner_task.navigation.base import go_to_freelancers_page, go_to_profile_page


def run(headless: bool):
    """
    Main execution flow, writing results to a file
    """
    logging.info('Scanner running...')
    driver = setup_webdriver(headless)

    if user_credentials := load_credentials():
        user = user_credentials[1]
    else:
        raise Exception('Unable to load user credentials from file --> scanner_task/resources/user_base.json')

    # get page sources using selenium
    try:
        # IMPORTANT pause execution here and set the network request block on the browser to 'www.upwork.com/Ss13U803*'
        cursor_movement = start_cursor_thread()

        authenticate(driver, user)

        try:
            go_to_freelancers_page(driver)
            sleep(6)
        except Exception as e:
            raise e
        else:
            page_source_to_file(driver, generate_new_filename('freelancers_page.html'))

        try:
            go_to_profile_page(driver, user)
            sleep(4)
        except Exception as e:
            raise e
        else:
            page_source_to_file(driver, generate_new_filename('contact_page.html'))

        kill_task(cursor_movement)
    except FileNotFoundError as e:
        logging.exception(e)
    finally:
        driver.close()

    # parse retrieved asynchronously sources saved on the PAGE_SOURCE_PATH, writing results to RESULT_PATH
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(parse_all_files(PAGE_SOURCE_PATH))
    except Exception as e:
        logging.exception(e)
    finally:
        loop.close()
