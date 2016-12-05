import gettext

import redis

from settings import REDIS

_langs = {}
_redis_db = None

def get_translate(lang='fa'):
    global _langs
    if lang in _langs:
        return _langs[lang]
    fa = gettext.translation('messages', localedir='locale', languages=[lang])
    fa.install()
    _langs[lang] = fa.gettext
    return _langs[lang]


def get_redis(db=0):
    global _redis_db
    if not _redis_db:
        _redis_db = redis.StrictRedis(db=db, **REDIS)
    return _redis_db

