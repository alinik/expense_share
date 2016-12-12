from raven import Client
from telegram import ReplyKeyboardMarkup
from telegram.contrib.botan import Botan

from settings import BOTAN_TOKEN, SENTRY_DSN

if SENTRY_DSN:
    client = Client(SENTRY_DSN)
else:
    client = None
botan = Botan(BOTAN_TOKEN)

from .server import start_bot
