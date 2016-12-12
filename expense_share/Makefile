all:
	pygettext **/*py
	msgcat locale/fa/LC_MESSAGES/messages.po | msgfmt -o locale/fa/LC_MESSAGES/messages.mo -
	msgcat locale/en/LC_MESSAGES/messages.po | msgfmt -o locale/en/LC_MESSAGES/messages.mo -
