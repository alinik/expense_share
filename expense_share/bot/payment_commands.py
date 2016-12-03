import locale
import logging
import gettext
from emoji import emojize
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup

from bot.commands import kbd_main_menu
from bot.states import ADD_PAYMENT, ADD_PAYMENT_2, CHOOSING, CALCULATOR
fa = gettext.translation('messages', localedir='locale', languages=['fa'])
fa.install()
_ = fa.gettext

def calc_kbd():
    return InlineKeyboardMarkup([InlineKeyboardButton(emojize(x, True), callback_data=x) for x in t] for t in
                                [[_('1'), _('2'), _('3')],
                                 [_('4'), _('5'), _('6')],
                                 [_('7'), _('8'), _('9')],
                                 [_(':arrow_backward:'), _('0'), _('000')],
                                 [_(':white_check_mark:')]])


def show_calculator(bot, update, user_data):
    query = update.callback_query
    user_data['calc'] = ''
    user_data['calc:orig_msg'] = query.data + _(' paid,')
    bot.editMessageText(
        text=user_data['calc:orig_msg'] + _(" how much?") + "\n ----------------------------------",
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=calc_kbd())
    bot.answerCallbackQuery(query.id)

    return CALCULATOR


def key_pressed(bot, update, user_data):
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
        reply_markup=calc_kbd())
    return CALCULATOR


def add_payment(bot, update, user_data=None):
    if not user_data['members']:
        update.message.reply_text(_('Please add some members first!'),reply_markup=kbd_main_menu)
        return CHOOSING
    user_data['uncommitted_payment'] = {'beneficiary': set(), 'amount': 0, 'description': '', 'payee': ''}
    members = InlineKeyboardMarkup([[InlineKeyboardButton(x, callback_data=x)] for x in user_data['members']])

    update.message.reply_text(_('Who Paid? '), reply_markup=members)
    return ADD_PAYMENT


def get_amount(bot, update, user_data=None, amount=0):
    query = update.callback_query
    members = InlineKeyboardMarkup(
        [[InlineKeyboardButton(emojize(':grey_question: %s ' % x, use_aliases=True), callback_data=x)] for x in
         user_data['members']])

    user_data['uncommitted_payment']['amount'] = int(amount)
    bot.editMessageText(
        text=_('%s Paid for %s, who was beneficiary?') % (user_data['uncommitted_payment']['payee'], amount),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=members)
    return ADD_PAYMENT_2


def choose_payee(bot, update, user_data=None):
    query = update.callback_query
    user_data['uncommitted_payment']['payee'] = query.data
    user_data['next state'] = get_amount
    bot.editMessageText(text=query.data + _("paid,"),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=calc_kbd())
    # bot.answerCallbackQuery(query.id)
    return show_calculator(bot, update, user_data)


def choose_beneficiary(bot, update, user_data=None):
    query = update.callback_query
    u = user_data['uncommitted_payment']
    if query.data == '!done':
        bot.editMessageText(
            text=_('So, %s paid %s for %s.') % (u['payee'], u['amount'], ','.join(u['beneficiary'])),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)
        bot.sendMessage(chat_id=query.message.chat_id, text=_('And anything to add or Done?'),
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[['Done']],
                            # keyboard=[['Add Location', 'Add Description'], ['Add Image', 'Done']],
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
    for item in user_data['members']:
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
    text = update.message.text
    u = user_data['uncommitted_payment']
    u['description'] += '\n' + text
    return ADD_PAYMENT_2


def submit_payment(bot, update, user_data):
    update.message.reply_text(_("Payment Added"), reply_markup=kbd_main_menu)
    payment = user_data['uncommitted_payment'].copy()
    payment['description'] = payment['description'][1:]
    user_data['payments'].append(payment)
    user_data['uncommitted_payment'] = {}
    return CHOOSING


def list_transactions(bot, update, user_data):
    response = ''
    for payment in user_data['payments']:
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
