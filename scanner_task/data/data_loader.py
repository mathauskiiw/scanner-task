# data_loader.py
# python
import json
import logging
import os
from typing import Optional, List
# project
from scanner_task.common.constants import CREDENTIALS_FILEPATH
from scanner_task.common.classes import User


def load_credentials(fp: str = CREDENTIALS_FILEPATH) -> Optional[List[User]]:
    """
    Load user credentials from a given .json file
    """
    if os.path.exists(CREDENTIALS_FILEPATH):
        with open(CREDENTIALS_FILEPATH, 'r') as credentials_file:
            try:
                users = [User(**x) for x in json.load(credentials_file)]
                return users
            except Exception:
                logging.error("credentials file parsing error - invalid json")
                return None
    else:
        logging.error("credentials file doesnt exist")
        return None
