import random

from settings import TOKEN, ADS_ID
from utils import get_redis

db = get_redis()

PUB_TOKEN = TOKEN.split(':')[0]


def add_member(uid):
    return db.sadd('BOT:' + PUB_TOKEN, uid)


def members_count():
    return db.scard('BOT:' + PUB_TOKEN)


def get_adv_key():
    return 'BOT:%s:ADS' % PUB_TOKEN


def get_ads(chat_id):
    add_ads = get_adv_key()
    my_ads = 'BOT:%s:SEEN_ADS:%s' % (PUB_TOKEN, chat_id)
    remain_ads = db.sdiff(add_ads, my_ads, my_ads)
    if not remain_ads:
        db.delete(my_ads)
        return ADS_ID
    item = random.choice(list(remain_ads))
    db.sadd(my_ads, item)
    return item.decode('utf-8').split(':')
