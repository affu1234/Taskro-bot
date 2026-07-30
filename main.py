import os
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

TOKEN = "8862372091:AAGrkIUg92IiZLIMDCbN43sxneygeyzWAWM"
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

users_db = {}
MASTER_CODES = ["TASK2026", "ADMIN123"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id in users_db:
        bot.reply_to(message, "ℹ️ **Aapka account pehle se active hai!**\nAap bot ka poora anand le sakte hain.")
    else:
        # Sundar UI aur Inline Button ke sath welcome message
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔑 Enter Invite Code", callback_data="ask_code"))
        markup.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/your_channel"))
        
        bot.send_message(
            message.chat.id, 
            "🚀 **Welcome to Task Bot!**\n\nIs exclusive platform par aane ke liye aapko ek valid **Invite Code** ki zaroorat hai.\n\nNeeche diye गए button par click karke code darj karein:", 
            reply_markup=markup,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "ask_code")
def callback_query(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✍️ Kripya apna valid **Invite Code** abhi yahan message me bhejiye:")
    bot.register_next_step_handler(msg, verify_invite_code)

def verify_invite_code(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    entered_code = message.text.strip()

    all_existing_codes = [data['my_code'] for data in users_db.values()]

    if entered_code in MASTER_CODES or entered_code in all_existing_codes:
        unique_code = f"TASK-{random.randint(1000, 9999)}"
        
        users_db[user_id] = {
            "name": user_name,
            "used_code": entered_code,
            "my_code": unique_code
        }
        
        bot.reply_to(
            message, 
            f"🎉 **Badhai ho, {user_name}!**\n\nAapka invite code safaltapoorvak verify ho gaya hai.\n\n🔑 **Aapka Unique Referral Code:** `{unique_code}`\n\nIse apne doston ke sath share karein aur aage ka safar shuru karein!",
            parse_mode="Markdown"
        )
    else:
        msg = bot.reply_to(message, "❌ **Galat Invite Code!**\n\nKripya sahi **Invite Code** dobara type karke bhejiye:")
        bot.register_next_step_handler(msg, verify_invite_code)

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run)
    t.start()
    
    bot.remove_webhook()
    bot.infinity_polling()
