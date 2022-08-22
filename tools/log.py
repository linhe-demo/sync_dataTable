import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %p"

logging.basicConfig(filename='../log/script.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')


def debug(data):
    logging.debug(data)


def info(data):
    logging.info(data)


def warning(data):
    logging.warning(data)


def error(data):
    logging.error(data)


def critical(data):
    logging.critical(data)
