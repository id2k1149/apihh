from hh_api import result_page
from hh_api import vacancy_salary
import telebot
from settings import TG_TOKEN, proxies
from telebot import apihelper

# при необходимости использовать прокси
# apihelper.proxy = proxies

bot = telebot.TeleBot(TG_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    greeting = "Hi there.\n" \
               "This bot will help you to find key skills for any vacancy. " \
               "Just write a vacancy name."
    bot.reply_to(message, greeting)


# find and download a file with skills
@bot.message_handler(commands=['file'])
def get_file(message):
    vacancy = ' '.join(message.text.split(' ')[1:])
    file_name = f"skills_for_{vacancy}.json"
    try:
        with open(f"{file_name}", 'r', encoding='utf-8') as data:
            bot.send_document(message.chat.id, data)
    except FileNotFoundError:
        bot.reply_to(message, f"Didn't find file.\n"
                              f" Please, start vacancy search")


# find salary for vacancy
@bot.message_handler(commands=['salary'])
def get_file(message):
    key_word = ' '.join(message.text.split(' ')[1:])
    salary = vacancy_salary(key_word, 1)
    bot.reply_to(message, f"OK, let's find salary for {key_word}.\n"
                          f"Please wait while searching....")
    bot.reply_to(message, salary)


# find key skills for vacancy
@bot.message_handler(content_types=['text'])
def vacancy_search(message):
    key_word = message.text
    bot.reply_to(message, f"OK, let's find key skills for {key_word}.\n"
                          f"Please wait while searching....")
    skills = result_page(key_word, 1)
    bot.reply_to(message, skills)


bot.polling()
