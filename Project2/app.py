import telebot
from config import TOKEN, keys
from extensions import ConversionException, CurrencyConverter

bot = telebot.TeleBot(TOKEN)
  
@bot.message_handler(commands = ['start', 'help'])
def help(message: telebot.types.Message):
    text = "Use this format to convert currencies:\n" \
    "<from> <to> <amount>\n\n" \
    "'amount' is any amount you want to convert\n\n" \
    "'from' and 'to' - can be one of the currencies available\n\n" \
    "Use /values to see a list of available currencies"
    
    bot.reply_to(message, text);

@bot.message_handler(commands = ['values'])
def values(message: telebot.types.Message):
    text = "Available currencies:"
    for key in keys.keys():
        text = '\n'.join((text, f'{key} - {keys[key]}'))
        
    bot.reply_to(message, text)
    
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.upper().split(' ')

        if len(values) != 3:
            raise ConversionException('Incorrect number of parameneters. Use /help for usage')

        base, quote, amount = values
        
        total = CurrencyConverter.get_price(base, quote, amount)
        
    except ConversionException as e:
        bot.reply_to(message, f'User error\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Failed to process command\n{e}')
    else:
        text = f'The price of {float(amount):,.2f} {base} ({keys[base]}) in {quote} ({keys[quote]}) is {total:,.2f}'
        bot.send_message(message.chat.id, text)
    
bot.polling()
