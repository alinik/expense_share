import gettext

langs = {}


def get_translate(lang='fa'):
    if lang in langs:
        return langs[lang]
    fa = gettext.translation('messages', localedir='locale', languages=[lang])
    fa.install()
    langs[lang] = fa.gettext
    return langs[lang]
