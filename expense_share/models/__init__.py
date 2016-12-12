import random

from models.Bot import get_adv_key, PUB_TOKEN
from settings import ADS_ID
from utils import get_redis
from . import User,Bot
db = get_redis()


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