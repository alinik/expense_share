import ujson

from utils import get_redis

db = get_redis()


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
