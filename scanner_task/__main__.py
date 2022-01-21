# __main.py__
# python
import logging

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
    app.run()
