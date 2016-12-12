import logging

from emoji import emojize
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup

import locale
import models
from bot.states import ADD_PAYMENT, ADD_PAYMENT_2, CHOOSING, CALCULATOR
from models import User



def calc_kbd(update):
    _ = User.get_my_lang(update)

    return InlineKeyboardMarkup([InlineKeyboardButton(emojize(x, True), callback_data=x) for x in t] for t in
                                [[_('1'), _('2'), _('3')],
                                 [_('4'), _('5'), _('6')],
                                 [_('7'), _('8'), _('9')],
                                 [_(':arrow_backward:'), _('0'), _('000')],
                                 [_(':white_check_mark:')]])


def show_calculator(bot, update, user_data):

    query = update.callback_query
    _ = User.get_my_lang(query)
    user_data['calc'] = ''
    user_data['calc:orig_msg'] = query.data + _(' paid,')
    bot.editMessageText(
        text=user_data['calc:orig_msg'] + _(" how much?") + "\n ----------------------------------",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=calc_kbd(query))
    bot.answerCallbackQuery(query.id)

    return CALCULATOR


def key_pressed(bot, update, user_data):
    _ = User.get_my_lang(update)

    query = update.callback_query
    if query.data == ':white_check_mark:':
        del user_data['calc:orig_msg']
        bot.answerCallbackQuery(query.id)

        return user_data.get('next state')(bot, update, user_data, user_data['calc'])
    if query.data == ':arrow_backward:':
        user_data['calc'] = user_data['calc'][:-1]
    else:
        user_data['calc'] += query.data
    bot.answerCallbackQuery(query.id)
    bot.editMessageText(
        text=user_data['calc:orig_msg'] + _(" how much?") + user_data['calc'],
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=calc_kbd(query))
    return CALCULATOR


def add_payment(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)


    members = models.User.get_members(update.message.chat_id)
    if not members:
        update.message.reply_text(_('Please add some members first!'), reply_markup=kbd_main_menu)
        return CHOOSING
    user_data['uncommitted_payment'] = {'beneficiary': set(), 'amount': 0, 'description': '', 'payee': ''}
    kbd_members = InlineKeyboardMarkup([[InlineKeyboardButton(x, callback_data=x)] for x in members])

    update.message.reply_text(_('Who Paid? '), reply_markup=kbd_members)
    return ADD_PAYMENT


def get_amount(bot, update, user_data=None, amount=0):
    _ = User.get_my_lang(update)
    query = update.callback_query or update
    members = models.User.get_members(query.message.chat_id)

    kbd_members = InlineKeyboardMarkup(
        [[InlineKeyboardButton(emojize(':grey_question: %s ' % x, use_aliases=True), callback_data=x)] for x in
         members])

    user_data['uncommitted_payment']['amount'] = int(amount)
    if update.callback_query:
        bot.editMessageText(
            text=_('%s Paid for %s, who was beneficiary?') % (user_data['uncommitted_payment']['payee'], amount),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=kbd_members)
    else:
        bot.sendMessage(
            text=_('%s Paid for %s, who was beneficiary?') % (user_data['uncommitted_payment']['payee'], amount),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=kbd_members)
    return ADD_PAYMENT_2


def choose_payee(bot, update, user_data=None):
    _ = User.get_my_lang(update)
    query = update.callback_query
    user_data['uncommitted_payment']['payee'] = query.data
    user_data['next state'] = get_amount
    bot.editMessageText(text=query.data + _("paid,"),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=calc_kbd(update))
    # bot.answerCallbackQuery(query.id)
    return show_calculator(bot, update, user_data)


# noinspection PyUnresolvedReferences
def choose_beneficiary(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    query = update.callback_query
    u = user_data['uncommitted_payment']
    if query.data == '!done':
        bot.editMessageText(
            text=_('So, %s paid %s for %s.') % (u['payee'], u['amount'], ','.join(u['beneficiary'])),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)
        bot.sendMessage(chat_id=query.message.chat_id, text=_('And anything to add or Done?'),
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[[_('Done'), _('Cancel')]],
                            resize_keyboard=True,
                            one_time_keyboard=True))
        bot.answerCallbackQuery(query.id)
        return ADD_PAYMENT_2
    member = query.data
    beneficiary = user_data['uncommitted_payment']['beneficiary']
    if member in beneficiary:
        beneficiary.remove(member)
    else:
        beneficiary.add(member)
    members_status = []
    percentage = 0
    if beneficiary:
        percentage = 100.0 / len(beneficiary)
    for item in models.User.get_members(query.message.chat_id):
        status = ':grey_question:'
        p = 0
        if item in beneficiary:
            status, p = ':point_right:', percentage
        members_status.append([InlineKeyboardButton(emojize("%s %s :%%%0.2f" % (status, item, p), use_aliases=True),
                                                    callback_data=item)])
    if beneficiary:
        members_status += [[InlineKeyboardButton(emojize(':white_check_mark: Done', True), callback_data='!done')]]
    kbd = InlineKeyboardMarkup(members_status)
    # update.callback_query.message.reply_text('Ok, who was beneficiary?', reply_markup=kbd)

    bot.editMessageText(text=_('So, %s paid %s for %s.') % (
        u['payee'], locale.format('%d', u['amount'], grouping=True), ','.join(u['beneficiary'])),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id, reply_markup=kbd)
    bot.answerCallbackQuery(query.id)
    logging.debug('beneficiary Status %r', beneficiary)
    return ADD_PAYMENT_2


def message(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    text = update.message.text
    u = user_data['uncommitted_payment']
    u['description'] += '\n' + text
    update.message.reply_text(_('And anything to add or Done?'))
    return ADD_PAYMENT_2


def submit_payment(bot, update, user_data):
    _ = User.get_my_lang(update)

    kbd_main_menu = ReplyKeyboardMarkup(
        keyboard=[[_('Add Member'), _('Add Payment')],
                  [_('Show Result'), _('List Transactions'), _('Help')],
                  [_('Lets Restart!')]],
        resize_keyboard=True,
        one_time_keyboard=True)


    if update.message.text in ['Cancel', _('Cancel')]:
        update.message.reply_text(_("Payment Cancelled"), reply_markup=kbd_main_menu)
    else:
        if not user_data['uncommitted_payment']['beneficiary']:
            return get_amount(bot, update, user_data, user_data['uncommitted_payment']['amount'])
        update.message.reply_text(_("Payment Added"), reply_markup=kbd_main_menu)
        payment = user_data['uncommitted_payment'].copy()
        payment['description'] = payment['description'][1:]
        models.User.add_payment(update.message.chat_id, payment)

    user_data['uncommitted_payment'] = {}
    return CHOOSING


# noinspection PyUnresolvedReferences
def list_transactions(bot, update, user_data):
    _ = User.get_my_lang(update)
    response = ''
    payments = models.User.get_payments(update.message.chat_id)

    for payment in payments:
        response += _('*%s* pays %s for *%s* ') % (
            payment['payee'], locale.format('%0.2f', payment['amount'], grouping=True),
            ','.join(payment['beneficiary']))
        if payment.get('description'):
            response += '_[%s]_' % payment['description']
        response += '.\n'
    if not response:
        response = _('The result is empty')
    update.message.reply_text(response, parse_mode='Markdown', reply_markup=kbd_main_menu)
    return CHOOSING
