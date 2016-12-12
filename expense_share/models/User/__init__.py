import ujson

from utils import get_redis, get_translate
from models.Bot import PUB_TOKEN

db = get_redis()

PREFIX = 'BOT:%s:USER' % PUB_TOKEN


def add_members(uid, member):
    return db.sadd('USER:%s:%s' % (uid, 'MEMBERS'), member)


def get_members(uid):
    members = [x.decode('utf-8') for x in db.smembers('USER:%s:%s' % (uid, 'MEMBERS')) if x]
    return members


def flush_members(uid):
    return db.delete('USER:%s:%s' % (uid, 'MEMBERS'))


def add_payment(uid, payment):
    return db.lpush('USER:%s:%s' % (uid, 'PAYMENTS'), ujson.dumps(payment))


def get_payments(uid):
    return [ujson.loads(x) for x in db.lrange('USER:%s:%s' % (uid, 'PAYMENTS'), 0, -1) if x]


def flush_payments(uid):
    return db.delete('USER:%s:%s' % (uid, 'PAYMENTS'))


def set_lang(uid, lang):
    return db.hset("%s:SETTINGS:%s" % (PREFIX, uid), "LANG", lang)


def get_lang(uid):
    return db.hget("%s:SETTINGS:%s" % (PREFIX, uid), "LANG")


def get_my_lang(update):
    uid = ''
    if update:
        if update.message:
            uid = update.message.chat_id
        elif update.callback_query:
            uid = update.callback_query.message.chat_id
    return get_translate(get_lang(uid))
