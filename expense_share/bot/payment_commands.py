import locale
import logging

from emoji import emojize
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup

from bot.calculator import calc_kbd, show_calculator
from bot.commands import kbd_main_menu
from bot.states import ADD_PAYMENT, ADD_PAYMENT_2, CHOOSING


def add_payment(bot, update, user_data=None):
    user_data['uncommitted_payment'] = {'beneficiary': set(), 'amount': 0, 'description': '', 'payee': ''}
    members = InlineKeyboardMarkup([[InlineKeyboardButton(x, callback_data=x)] for x in user_data['members']])

    update.message.reply_text('Who Paid? ', parse_mode='Markdown',
                              reply_markup=members)
    return ADD_PAYMENT


def get_amount(bot, update, user_data=None, amount=0):
    query = update.callback_query
    members = InlineKeyboardMarkup(
        [[InlineKeyboardButton(emojize(':grey_question: %s ' % x, use_aliases=True), callback_data=x)] for x in
         user_data['members']])

    user_data['uncommitted_payment']['amount'] = int(amount)
    bot.editMessageText(
        text='%s Paid for %s, who was beneficiary?' % (user_data['uncommitted_payment']['payee'], amount),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=members)
    return ADD_PAYMENT_2


def choose_payee(bot, update, user_data=None):
    query = update.callback_query
    user_data['uncommitted_payment']['payee'] = query.data
    user_data['next state'] = get_amount
    bot.editMessageText(text="%s paid," % query.data,
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
            text='So, %s paid %s for %s.' % (u['payee'], u['amount'], ','.join(u['beneficiary'])),
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)
        bot.sendMessage(chat_id=query.message.chat_id, text='And anything to add or Done?',
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[['Done']],
                            # keyboard=[['Add Location', 'Add Description'], ['Add Image', 'Done']],
                            resize_keyboard=True,
                            one_time_keyboard=True))
        bot.answerCallbackQuery(query.id)
        # bot.editMessageText(text='Ok, Is there any comment, location or image you need to share?',
        #                     chat_id=query.message.chat_id,
        #                     message_id=query.message.message_id,
        #                     reply_markup=ReplyKeyboardMarkup([['Done']], resize_keyboard=True, one_time_keyboard=True))
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

    bot.editMessageText(text='So, %s paid %s for %s.' % (
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
    update.message.reply_text("Payment Added", reply_markup=kbd_main_menu)
    payment = user_data['uncommitted_payment'].copy()
    payment['description']=payment['description'][1:]
    user_data['payments'].append(payment)
    user_data['uncommitted_payment'] = {}
    return CHOOSING


