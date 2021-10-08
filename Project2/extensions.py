import requests
import json
from config import API_KEY, keys

class ConversionException(Exception):
    pass

    
class CurrencyConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConversionException(f'No rates for such currency <{base}> found. Use /values to see available currencies')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConversionException(f'No rates for such currency <{quote}> found. Use /values to see available currencies')

        if base == quote:
            raise ConversionException(f'The currencies are the same <{base}>')

        try:
            amount = float(amount)
        except ValueError:
            raise ConversionException(f'Wrong amount <{amount}>')
        
        url = f'http://api.exchangeratesapi.io/v1/latest?access_key={API_KEY}&symbols={base},{quote}'
        resp = requests.get(url)
        
        base_val = json.loads(resp.content)['rates'][base]
        quote_val = json.loads(resp.content)['rates'][quote]
        
        total = amount * float(quote_val) / float(base_val)
        
        return total
        