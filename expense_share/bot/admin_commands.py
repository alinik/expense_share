# noinspection PyUnresolvedReferences
import logging

from ownbot.auth import assign_first_to, requires_usergroup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

import models
from bot import states, botan, client
from models import User
from settings import ADMIN_IDS


def choose_lang(bot, update):
    _ = User.get_my_lang(update)
    update.message.reply_text('Please choose your language\n%s' % _("Please choose your language"),
                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('English', callback_data='en'),
                                                                  InlineKeyboardButton(_('Persian'),
                                                                                       callback_data='fa'), ]]))
    return states.CHOOSE_LANG


def choose_lang_cb(bot, update, user_data=None):
    query = update.callback_query
    if query and query.data == 'fa':
        models.User.set_lang(query.message.chat_id, 'fa')
    else:
        models.User.set_lang(query.message.chat_id, 'en')
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)
    bot.answerCallbackQuery(query.id)
    bot.editMessageText(
        text=_("You choose English for your default lang"),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
    update.message.reply_markup(_('OK Lets start'),
                                reply_markup=kbd_main_menu)
    return states.CHOOSING


@assign_first_to("admin")
def start(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)

    for ids in ADMIN_IDS:
        bot.sendMessage(chat_id=ids, text='New user joined. %s %s (@%s)' % (
            update.message.chat.first_name, update.message.chat.last_name,
            update.message.chat.username))

    logging.info('START chat: %s', update.message.chat_id)
    botan.track(update.message, '/start')
    update.message.reply_text(_("Hi, I will calculate your Expense Share"),
                              reply_markup=kbd_main_menu)
    user_data.clear()
    models.User.flush_members(update.message.chat_id)
    models.User.flush_payments(update.message.chat_id)
    models.Bot.add_member(update.message.chat_id)
    return choose_lang(bot, update)


def send_ads(bot, update, user_data):
    # FIXME: per language
    from_user, adv_id = models.get_ads(update.message.chat_id)
    bot.forwardMessage(chat_id=update.message.chat_id, from_chat_id=from_user, message_id=adv_id)
    return


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))
    result = {}
    if update:
        result = update.to_dict()
    if client:
        client.captureMessage(error, extra={'update': result})


def welcome_admins(bot, admin_ids):
    members_count = models.Bot.members_count()
    for admin_id in admin_ids:
        bot.sendMessage(chat_id=admin_id,
                        text='Starting bot...\n\n\n*Bot started with %s users*\n\n\nHello *Admin*' % members_count,
                        parse_mode='Markdown')


@requires_usergroup("admin", "managers")
def report_msg(bot, update):
    update.message.reply_text("This message has following ID for Bot:  %s" % models.Bot.get_adv_key())
    update.message.reply_text("%s:%s" % (update.message.chat_id, update.message.message_id))
