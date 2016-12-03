import gettext
import logging

from emoji import emojize
from ownbot.auth import assign_first_to
from raven import Client
from telegram import ReplyKeyboardMarkup
from telegram.contrib.botan import Botan

from bot.states import CHOOSING, ADD_MEMBER
from calculator import calculate_owns
from calculator import optimized
from settings import BOTAN_TOKEN, ADMIN_IDS, SENTRY_DSN

client = Client(SENTRY_DSN)

fa = gettext.translation('messages', localedir='locale', languages=['fa'])
fa.install()
_ = fa.gettext

kbd_main_menu = ReplyKeyboardMarkup(
    keyboard=[[_('Add Member'), _('Add Payment')], [_('Show Result'), _('List Transactions'), _('Help')]],
    resize_keyboard=True,
    one_time_keyboard=True)
botan = Botan(BOTAN_TOKEN)


def reset(bot, update, user_data):
    user_data.clear()
    user_data['payments'] = []
    user_data['members'] = set()
    update.message.reply_text(_("Let's Start ..."), reply_markup=kbd_main_menu)

    return CHOOSING


@assign_first_to("admin")
def start(bot, update, user_data=None):
    for ids in ADMIN_IDS:
        bot.sendMessage(chat_id=ids, text='New user joined. %s %s (@%s)' % (
            update.message.chat.first_name, update.message.chat.last_name,
            update.message.chat.username))
    logging.info('START chat: %s', update.message.chat_id)
    botan.track(update.message, '/start')
    update.message.reply_text(_("Hi, I will calculate your Expense Share"),
                              reply_markup=kbd_main_menu)
    user_data.clear()
    user_data['payments'] = []
    user_data['members'] = set()
    return CHOOSING


def cmd_main_menu(bot, update, user_data):
    pass


def show_result(bot, update, user_data):
    response = ''
    botan.track(update.message, 'show result')
    for payer, payee, amount in optimized(calculate_owns(user_data)):
        response += _('%s :arrow_right: %s :moneybag: %s\n') % (payer, payee, amount)
    if not response:
        response = _('The result is empty')
    update.message.reply_text(emojize(response, True),reply_markup=kbd_main_menu)
    return CHOOSING


def add_member(bot, update, user_data=None):
    logging.info('ADDMEMBER chat: %s', update.message.chat_id)
    bot.sendMessage(chat_id=update.message.chat_id, text=_('Please type new Member Name'))
    return ADD_MEMBER


def add_member_cb(bot, update, user_data=None):
    text = update.message.text
    contact = update.message.contact
    if contact:
        logging.info('ADD_MEMBER_CB received:[contact] %s', contact.first_name)
        member = contact.first_name
    else:
        logging.info('ADD_MEMBER_CB received: %s', text)
        member = text
    user_data['members'].add(member)
    logging.info('Members: %s', user_data['members'])
    bot.sendMessage(chat_id=update.message.chat_id, text=_('Aha'), reply_markup=kbd_main_menu)
    return CHOOSING


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

    client.captureMessage(error, extra={'update':update.to_dict()})


def welcome_admins(bot, admin_ids):
    for admin_id in admin_ids:
        bot.sendMessage(chat_id=admin_id, text='Starting bot...\n\n\n*Bot started*\n\n\nHello *Admin*',
                        parse_mode='Markdown')


def done(bot, update, user_data):
    update.message.reply_text(_("Lets Restart!"), reply_markup=kbd_main_menu)
    user_data.clear()
    return CHOOSING
