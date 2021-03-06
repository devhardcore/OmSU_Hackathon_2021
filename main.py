from time import sleep

import logger


def main():
    while True:
        logger.show_msg("Hello world!")
        sleep(6)


if __name__ == '__main__':
    main()
