from emoji import emojize
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from bot import states


def calc_kbd():
    return InlineKeyboardMarkup([InlineKeyboardButton(emojize(x, True), callback_data=x) for x in t] for t in
                                [['1', '2', '3'],
                                 ['4', '5', '6'],
                                 ['7', '8', '9'],
                                 [':arrow_backward:', '0', '000'],
                                 [':white_check_mark:']])


def show_calculator(bot, update, user_data):
    query = update.callback_query
    user_data['calc'] = ''
    user_data['calc:orig_msg'] = query.data + ' paid,'
    bot.editMessageText(text="%s paid, how much? \n ----------------------------------" % query.data,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=calc_kbd())
    bot.answerCallbackQuery(query.id)

    return states.CALCULATOR


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
        user_data['calc:orig_msg'] + ' how much? %s\n ----------------------------------' % user_data['calc'],
        chat_id=query.message.chat_id,
        message_id=query.message.message_id, reply_markup=calc_kbd())
    return states.CALCULATOR
