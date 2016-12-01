import logging

from ownbot.auth import assign_first_to
from telegram import ReplyKeyboardMarkup

from bot.states import CHOOSING, ADD_MEMBER

kbd_main_menu = ReplyKeyboardMarkup(keyboard=[['Add Member', 'Add Payment'], ['Show Result', 'Help']],
                                    resize_keyboard=True,
                                    one_time_keyboard=True)


@assign_first_to("admin")
def start(bot, update, user_data=None):
    logging.info('START chat: %s', update.message.chat_id)
    update.message.reply_text("Hi, I will calculate your Share Rate",
                              reply_markup=kbd_main_menu)
    user_data['payments'] = []
    user_data['members'] = set()
    return CHOOSING


def cmd_main_menu(bot, update, user_data):
    pass


def add_member(bot, update, user_data=None):
    logging.info('ADDMEMBER chat: %s', update.message.chat_id)
    bot.sendMessage(chat_id=update.message.chat_id, text='Please type new Member Name')
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
    bot.sendMessage(chat_id=update.message.chat_id, text='Aha', reply_markup=kbd_main_menu)
    return CHOOSING


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


def welcome_admins(bot, admin_ids):
    for admin_id in admin_ids:
        bot.sendMessage(chat_id=admin_id, text='Starting bot...\n\n\n*Bot started*\n\n\nHello *Admin*',
                        parse_mode='Markdown')


def done(bot, update, user_data):
    update.message.reply_text("Lets Restart!", reply_markup=kbd_main_menu)
    user_data.clear()
    return CHOOSING