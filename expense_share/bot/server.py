from gettext import gettext as _
from ownbot.admincommands import AdminCommands
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Updater
import gettext
from bot import states
# from bot.calculator import key_pressed
from .commands import start, add_member, add_member_cb, error, welcome_admins, show_result, reset
from .payment_commands import add_payment, choose_payee, get_amount, choose_beneficiary, message, submit_payment, \
    list_transactions, key_pressed

fa = gettext.translation('messages', localedir='locale', languages=['fa'])
fa.install()
_ = fa.gettext

def start_bot(token, admin_ids):
    updater = Updater(token)
    dp = updater.dispatcher
    AdminCommands(dp)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            states.CHOOSING: [
                RegexHandler('^(Show Result|%s)$'%_('Show Result'),
                             show_result,
                             pass_user_data=True),
                RegexHandler('^(Add Member|%s)$'%_('Add Member'),
                             add_member, pass_user_data=True),
                MessageHandler(Filters.contact,
                               add_member, pass_user_data=True),
                RegexHandler('^(Add Payment|%s)$'%_('Add Payment'),
                             add_payment, pass_user_data=True),
                RegexHandler('^(List Transactions|%s)$'%_('List Transactions'),
                             list_transactions, pass_user_data=True),

            ],

            states.ADD_MEMBER: [
                MessageHandler(Filters.text,
                               add_member_cb,
                               pass_user_data=True),
            ],

            states.ADD_PAYMENT: [
                MessageHandler(Filters.text,
                               get_amount,
                               pass_user_data=True),
                CallbackQueryHandler(choose_payee, pass_user_data=True)
            ],
            states.ADD_PAYMENT_2: [
                RegexHandler('^(Done|%s)$'%_("Done"), submit_payment, pass_user_data=True),
                CallbackQueryHandler(choose_beneficiary, pass_user_data=True),
                MessageHandler(Filters.all, message, pass_user_data=True),
            ],
            states.CALCULATOR: [
                CallbackQueryHandler(key_pressed, pass_user_data=True),
            ],

        },

        fallbacks=[
            CommandHandler('reset', reset, pass_user_data=True),
            MessageHandler(Filters.all, reset,pass_user_data=True),
        ]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    welcome_admins(dp.bot, admin_ids)
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
