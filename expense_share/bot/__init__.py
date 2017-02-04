from raven import Client
from telegram import ReplyKeyboardMarkup
from telegram.contrib.botan import Botan

from settings import BOTAN_TOKEN, SENTRY_DSN

if SENTRY_DSN:
    client = Client(SENTRY_DSN)
else:
    client = None
botan = Botan(BOTAN_TOKEN)


def default_menu(_):
    return ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Select Language')+' '+_('en')],
                  [_('Lets Restart!'),_('Help')]],
        resize_keyboard=True,
        one_time_keyboard=True)


from .server import start_bot
