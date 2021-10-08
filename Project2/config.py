from requests import get
from json import loads
TOKEN = '1966318085:AAHtNJdWjSTj58RfyM10jAr5wzsYbmRmhiI'
API_KEY = '7938d49902c6709e5f81b3921271272d'

keys = loads(get(f'http://api.exchangeratesapi.io/v1/symbols?access_key={API_KEY}'). \
    content)['symbols']
