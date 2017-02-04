import ujson

from utils import get_redis, get_translate
from models.Bot import PUB_TOKEN

db = get_redis()

PREFIX = 'BOT:%s:U' % PUB_TOKEN


def add_members(uid, member):
    return db.sadd('U:%s:%s' % (uid, 'MEMBERS'), member)


def get_members(uid):
    members = [x.decode('utf-8') for x in db.smembers('U:%s:%s' % (uid, 'MEMBERS')) if x]
    return members


def flush_members(uid):
    return db.delete('U:%s:%s' % (uid, 'MEMBERS'))


def add_payment(uid, payment):
    return db.lpush('U:%s:%s' % (uid, 'PAYMENTS'), ujson.dumps(payment))


def get_payments(uid):
    return [ujson.loads(x) for x in db.lrange('U:%s:%s' % (uid, 'PAYMENTS'), 0, -1) if x]


def flush_payments(uid):
    return db.delete('U:%s:%s' % (uid, 'PAYMENTS'))


def set_lang(uid, lang):
    retval =  db.hset("%s:S:%s" % (PREFIX, uid), "LANG", lang)
    return retval


def get_lang(uid):
    return db.hget("%s:S:%s" % (PREFIX, uid), "LANG")


def set_first_use(uid, status=True):
    return db.hset("%s:S:%s" % (PREFIX, uid), "FIRST_USE", status)


def get_first_use(uid):
    t = db.hget("%s:S:%s" % (PREFIX, uid), "FIRST_USE")
    db.hset("%s:S:%s" % (PREFIX, uid), "FIRST_USE",None)
    return t


def get_my_lang(update):
    uid = ''
    if update:
        if update.message:
            uid = update.message.chat_id
        elif update.callback_query:
            uid = update.callback_query.message.chat_id
    return get_translate(get_lang(uid))
