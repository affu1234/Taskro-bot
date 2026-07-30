import os
import random
import telebot
from flask import Flask

TOKEN = "8862372091:AAGrkIUg92IiZLIMDCbN43sxneygeyzWAWM"
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

# Temporary list/memory data (Jab tak sheet fix na ho)
users_db = {}
MASTER_CODES = ["TASK2026", "ADMIN123"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id in users_db:
        bot.reply_to(message, "ℹ️ **Aap pehle se registered hain!**\n\nAapka account active hai.")
    else:
        msg = bot.reply_to(message, "👋 **Welcome!**\n\nIs bot par access paane ke liye kripya apna valid **Invite Code** enter karein:")
        bot.register_next_step_handler(msg, verify_invite_code)

def verify_invite_code(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    entered_code = message.text.strip()

    # Check codes
    all_existing_codes = [data['my_code'] for data in users_db.values()]

    if entered_code in MASTER_CODES or entered_code in all_existing_codes:
        unique_code = f"TASK-{random.randint(1000, 9999)}"
        
        users_db[user_id] = {
            "name": user_name,
            "used_code": entered_code,
            "my_code": unique_code
        }
        
        bot.reply_to(message, f"✅ **Registration Successful!**\n\nBadhai ho {user_name}, aapka invite code verify ho chuka hai.\n\n🔑 **Aapka Unique Invite Code:** `{unique_code}`")
    else:
        msg = bot.reply_to(message, "❌ **Invalid Invite Code!**\n\nYe code galat hai. Kripya sahi **Invite Code** dobara bhejiye:")
        bot.register_next_step_handler(msg, verify_invite_code)

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run)
    t.start()
    
    bot.remove_webhook()
    bot.infinity_polling()
