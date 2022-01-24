# __main.py__
# python
import logging
import sys

# project
from scanner_task import app
from scanner_task.common.constants import LOG_PATH

if __name__ == '__main__':
    logging.basicConfig(
        filename=LOG_PATH,
        filemode='a',
        format='%(asctime)s | %(levelname)s >> %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    headless = True if "--headless" in sys.argv else False
    app.run(headless)
