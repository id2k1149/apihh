from main import result_page
import telebot
from settings import TG_TOKEN, proxies
from telebot import apihelper

# при необходимости использовать прокси
apihelper.proxy = proxies

bot = telebot.TeleBot(TG_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    greeting = "Hi there.\nThis bot will help you to find key skills for any vacancy. Just write a vacancy name."
    bot.reply_to(message, greeting)


# find skills_for file
@bot.message_handler(commands=['file'])
def get_file(message):
    vacancy = ' '.join(message.text.split(' ')[1:])
    file_name = f"file_{vacancy}.json"
    try:
        with open(f"{file_name}", 'r', encoding='utf-8') as data:
            bot.send_document(message.chat.id, data)
    except FileNotFoundError:
        bot.reply_to(message, f"Didn't find file.\nPlease, start vacancy search")


# find key skills for vacancy
@bot.message_handler(content_types=['text'])
def vacancy_search(message):
    key_word = message.text
    bot.reply_to(message, f"OK, let's find key skills for {key_word}")
    bot.reply_to(message, 'Please wait while searching....')
    skills = result_page(key_word)
    bot.reply_to(message, skills)


bot.polling()
