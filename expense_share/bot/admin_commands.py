# noinspection PyUnresolvedReferences
import logging

from ownbot.auth import assign_first_to, requires_usergroup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup

import models
import utils
from bot import states, botan, client, default_menu
from models import User
from models.User import get_first_use
from settings import ADMIN_IDS


def choose_lang(bot, update):
    _ = utils.get_translate('fa')
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

    kbd_main_menu = default_menu(_)
    bot.answerCallbackQuery(query.id)
    bot.editMessageText(
        text=_("You choose English for your default lang"),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
    if get_first_use(query.message.chat_id):
        show_help(bot, update.callback_query, None)

    bot.sendMessage(text=_('OK Lets start'), chat_id=query.message.chat_id,
                    reply_markup=kbd_main_menu)
    return states.CHOOSING


@assign_first_to("admin")
def start(bot, update, user_data=None):
    _ = User.get_my_lang(update)

    kbd_main_menu = default_menu(_)

    for ids in ADMIN_IDS:
        bot.sendMessage(chat_id=ids, text='New user joined. %s %s (@%s)' % (
            update.message.chat.first_name, update.message.chat.last_name,
            update.message.chat.username))

    logging.info('START chat: %s', update.message.chat_id)
    botan.track(update.message, '/start')
    user_data.clear()
    models.User.flush_members(update.message.chat_id)
    models.User.flush_payments(update.message.chat_id)
    models.User.set_first_use(update.message.chat_id)
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


def show_help(bot, update, user_data):
    help = {
        b'fa': '''
من يك ربات هستم كه براى انجام حساب كتاب هاى مشترك ميتونم بهت كمك كنم. كار كردن با من خيلى ساده هست.

١- اول دكمه 'شروع حساب كتاب جديد' رو بزن. با اين كار من آماده انجام كار ميشم.

٢- دكمه 'افزودن فرد' رو بزن. با زدن اين دكمه من اسم اشخاصى كه توى اين حساب كتاب شريك و سهيم هستند رو ازت ميپرسم.
 وقتى دكمه 'افزودن فرد' رو ميزنى من اسم شخاص سهيم در حساب كتاب فعلى رو ازت ميپرسم و به ليست افراد اضافه ميكنم.
نكته مهم: توصيه ميكنم قبل وارد كردن هزينه ها اول همه افراد سهيم رو با استفاده از اين دكمه وارد كنى.

٣- حالا كه همه افراد رو وارد كردى نوبت به وارد كردن هزينه هاى انجام شده ميرسه. براى اين كهر دكمه 'افزودن هزينه' رو بزن.
- وقتى اين دكمه رو زدى من ازت ميپرسم كه چه كسى اين هزينه رو انجام داده و ليست همه افراد رو نشونت ميدم تا بتونى اون شخص رو از بينشون انتخاب كنى. (مثلاً على)
- وقتى شخص مورد نظر انتخاب شد حالا ازت ميپرسم كه چقدر هزينه كرده و يه صفحه كليد نشونت ميدم تا بتونى مبلغ هزينه شده رو وارد كنى. يادت باشه بعد از اينكه هزينه رو وارد كردى دكمه تيك سبزرنگ پايين صفحه رو بزن.
- حالا وقتشه كه به من بگى اين هزينه براى كيا انجام شده. يعنى چه افرادى تو اين هزينه خاص سهيم هستن. (مثلاً اگه على ١٠٠٠٠ تومن دادن و براى ٤ نفر بستنى خريده اينجا رو اسم تك تك اون افراد كليك كن. من همون لحظه به صورت همزمان بهت نشون ميدم كه هر شخص چند درصد از هزينه رو سهيم هست.
نكته مهم: اگه اسم كسى رو اشتباه انتخاب كردى براى اينكه از ليست اين هزينه حذفش كنى كافيه يه بار ديگه روش كليك كنى.
نكته مهم: همه هزينه ها رو به اين روش وارد كن.

٤- حالا كه همه هزينه ها رو وارد كردى وقتشه تا من به حساب كتابا برسم. دكمه 'نمايش نتايج رو بزن' تا من به صورت مختصر و مفيد بهت نشون بدم كه هر كسى چقدر به چه كسى بدهكار هست.
 ''',
        b'en': '''Hey Buddy!

Im here to help you and your friends settle expenses after a night out or any other sort of gathering. Its so simple, just follow these few steps:

1- Press the “Start” or “Restart” button to begin the process.

2- Press the “Add member” button and add as many people as you want to the list of people who are involved.

3- Once you’ve added all members, press the “Add Payment” button to start adding transactions and expenses. (Here you will tell me who paid how much for whom).

4- Finally when you are done entering all the payments, simply press the “Show results” button so i can quickly figure out who owes whom. THAT SIMPLE!

5- This bot is available in both English and Persian languages. If you will your language to be supported by our bot, please contact us.

'''
    }
    _ = User.get_my_lang(update)

    kbd_main_menu = default_menu(_)
    update.message.reply_text(help[User.get_lang(update.message.chat_id or b'en')], reply_markup=kbd_main_menu)
