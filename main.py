import os
import telebot
from flask import Flask

# Aapka Telegram Bot Token
TOKEN = "8862372091:AAGrkIUg92IiZLIMDCbN43sxneygeyzWAWM"
bot = telebot.TeleBot(TOKEN)

# Flask server taaki Render service active rahe (Web Service ke liye zaroori hai)
app = Flask('')

@app.route('/')
def home():
    $return "Bot is alive and running!"$

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"Hello {user_name}! Welcome to Taskro_x_bot. Aapka database connection jald hi active ho raha hai.")

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run)
    t.start()
    bot.infinity_polling()
