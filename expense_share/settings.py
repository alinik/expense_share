TOKEN = '299575654:AAES9AQaiVKx_4tMc8W2ETvaXChLYwd2qTk'
BOTAN_TOKEN = 'edzfzK:BfB7t-akoGiiiakPzl2Ds_e-D'
SENTRY_DSN = 'https://ebc8140116a04e8886fb4bf3e01131e1:4dd7f6d710544f508950250fb5b139a5@sentry.io/119423'
ADMIN_IDS = [110876335, ]
REDIS = {'unix_socket_path': '/var/run/redis/redis.sock'}
ADS_ID = (110876335, 3000)
try:
    from  local_settings import *
except ImportError:
    pass
