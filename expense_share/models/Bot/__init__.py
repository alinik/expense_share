from settings import TOKEN
from utils import get_redis

db = get_redis()

PUB_TOKEN = TOKEN.split(':')[0]


def add_member(uid):
    return db.sadd('BOT:' + PUB_TOKEN, uid)


def members_count():
    return db.scard('BOT:' + PUB_TOKEN)


def get_adv_key():
    return 'BOT:%s:ADS' % PUB_TOKEN


