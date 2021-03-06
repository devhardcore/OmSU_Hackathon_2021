import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def show_msg(msg: str):
    logging.info(msg)
