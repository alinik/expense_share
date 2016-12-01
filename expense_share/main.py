import locale
import logging


from bot import start_bot

from settings import TOKEN, ADMIN_IDS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
locale.setlocale(locale.LC_ALL, 'en_US..UTF-8')

if __name__ == '__main__':
    logging.info('Start Listening')
    start_bot(TOKEN, ADMIN_IDS)
