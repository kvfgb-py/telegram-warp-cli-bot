from dotenv import load_dotenv
import os
import telebot

load_dotenv('config.env')

bot_token = os.environ.get('BOT_TOKEN')
admin_id = int(os.environ.get('ADMIN_ID'))

bot = telebot.TeleBot(bot_token)