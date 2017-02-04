from ownbot.admincommands import AdminCommands
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Updater

from bot import states
from bot.admin_commands import start, error, welcome_admins, report_msg, choose_lang_cb, choose_lang, show_help
from bot.commands import bad_command
from utils import get_translate
from .commands import add_member, add_member_cb, show_result, reset
from .payment_commands import add_payment, choose_payee, choose_beneficiary, message, submit_payment, list_transactions, \
    key_pressed

_ = get_translate('fa')


def start_bot(token, admin_ids):
    updater = Updater(token)
    dp = updater.dispatcher
    AdminCommands(dp)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True),
                      MessageHandler(Filters.all, bad_command, pass_user_data=True)],

        states={
            states.CHOOSING: [

                RegexHandler('^(Show Result|%s)$' % _('Show Result'),
                             show_result,
                             pass_user_data=True),
                RegexHandler('^(Select Language|%s)' % _('Select Language'),
                             choose_lang),
                RegexHandler('^(Lets Restart!|%s)$' % _('Lets Restart!'),
                             reset,
                             pass_user_data=True),
                RegexHandler('^(Add Member|%s)$' % _('Add Member'),
                             add_member, pass_user_data=True),
                RegexHandler('^(Add Payment|%s)$' % _('Add Payment'),
                             add_payment, pass_user_data=True),
                RegexHandler('^(List Transactions|%s)$' % _('List Transactions'),
                             list_transactions, pass_user_data=True),
                MessageHandler(Filters.forwarded, report_msg)
            ],

            states.ADD_MEMBER: [
                MessageHandler(Filters.text,
                               add_member_cb,
                               pass_user_data=True),
                MessageHandler(Filters.contact,
                               add_member_cb, pass_user_data=True),

            ],

            states.ADD_PAYMENT: [
                # MessageHandler(Filters.text,
                #                get_amount,
                #                pass_user_data=True),
                CallbackQueryHandler(choose_payee, pass_user_data=True),
                MessageHandler(Filters.all, bad_command, pass_user_data=True),

            ],
            states.ADD_PAYMENT_2: [
                RegexHandler('^(Done|Cancel|%s|%s)$' % (_("Done"), _('Cancel')), submit_payment, pass_user_data=True),
                CallbackQueryHandler(choose_beneficiary, pass_user_data=True),
                MessageHandler(Filters.all, message, pass_user_data=True),
            ],
            states.CALCULATOR: [
                CallbackQueryHandler(key_pressed, pass_user_data=True),
                MessageHandler(Filters.all, bad_command, pass_user_data=True),

            ],
            states.CHOOSE_LANG: [
                CallbackQueryHandler(choose_lang_cb, pass_user_data=True),

            ]

        },

        fallbacks=[
            CommandHandler('reset', reset, pass_user_data=True),
            CommandHandler('lang', choose_lang),
            CommandHandler('start', start, pass_user_data=True),
            CommandHandler('help', show_help, pass_user_data=True),
            RegexHandler('^(Help|%s)$' % _('Help'),
                         show_help, pass_user_data=True),

            MessageHandler(Filters.all, bad_command, pass_user_data=True),
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
