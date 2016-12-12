import logging

from emoji import emojize
from telegram import ReplyKeyboardMarkup

import models
from bot import states, botan
from bot.admin_commands import send_ads
from bot.states import CHOOSING, ADD_MEMBER
from calculator import calculate_owns
from calculator import optimized
from models import User
from settings import ADMIN_IDS
from utils import get_translate

_ = get_translate('fa')


def reset(bot, update, user_data):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)


    user_data.clear()
    models.User.flush_members(update.message.chat_id)
    models.User.flush_payments(update.message.chat_id)
    update.message.reply_text(_("Let's Start ..."), reply_markup=kbd_main_menu)

    return CHOOSING


def show_result(bot, update, user_data):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)

    response = ''
    botan.track(update.message, 'show result')
    members = models.User.get_members(update.message.chat_id)
    payments = models.User.get_payments(update.message.chat_id)

    for payer, payee, amount in optimized(calculate_owns(members, payments)):
        response += _('User %s :arrow_right: %s :moneybag: %s\n') % (payer, payee, amount)
    if not response:
        response = _('The result is empty')
    update.message.reply_text(emojize(response, True), reply_markup=kbd_main_menu)
    send_ads(bot, update, user_data)
    return CHOOSING


def add_member(bot, update, user_data=None):
    _ = User.get_my_lang(update)
    logging.info('ADDMEMBER chat: %s', update.message.chat_id)
    bot.sendMessage(chat_id=update.message.chat_id, text=_('Please type new Member Name'))
    return ADD_MEMBER


def add_member_cb(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)


    text = update.message.text
    contact = update.message.contact
    if contact:
        logging.info('ADD_MEMBER_CB received:[contact] %s', contact.first_name)
        member = contact.first_name
    else:
        logging.info('ADD_MEMBER_CB received: %s', text)
        member = text
    models.User.add_members(update.message.chat_id, member)
    bot.sendMessage(chat_id=update.message.chat_id, text=_('Aha'), reply_markup=kbd_main_menu)
    return CHOOSING


def bad_command(bot, update, user_data):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)


    update.message.reply_text(_("I couldn't understand!"), reply_markup=kbd_main_menu)
    for admin_id in ADMIN_IDS:
        bot.forwardMessage(chat_id=admin_id, from_chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
    return states.CHOOSING
