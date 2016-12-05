from settings import TOKEN
from utils import get_redis

db = get_redis()


def add_member(uid):
    return db.sadd('BOT:' + TOKEN.split(':')[0], uid)


def members_count():
    return db.scard('BOT:' + TOKEN.split(':')[0])
