import os
import random
import telebot
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "8862372091:AAGrkIUg92IiZLIMDCbN43sxneygeyzWAWM"
bot = telebot.TeleBot(TOKEN)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("Bot_Database").worksheet("Users")

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

# Sabse pehla master invite code
MASTER_CODES = ["TASK2026", "ADMIN123"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    try:
        existing_user = sheet.find(user_id)
    except:
        existing_user = None

    if existing_user:
        bot.reply_to(message, "ℹ️ **Aap pehle se registered hain!**\n\nAapka account active hai aur aap bot ka use kar sakte hain.")
    else:
        msg = bot.reply_to(message, "👋 **Welcome!**\n\nIs bot par access paane ke liye kripya apna valid **Invite Code** enter karein:")
        bot.register_next_step_handler(msg, verify_invite_code)

def verify_invite_code(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    entered_code = message.text.strip()

    all_records = sheet.get_all_records()
    existing_codes = [str(row.get('My_Invite_Code')) for row in all_records if 'My_Invite_Code' in row]

    if entered_code in MASTER_CODES or entered_code in existing_codes:
        unique_code = f"TASK-{random.randint(1000, 9999)}"
        
        sheet.append_row([user_id, user_name, entered_code, unique_code])
        
        bot.reply_to(message, f"✅ **Registration Successful!**\n\nBadhai ho {user_name}, aapka invite code verify ho chuka hai.\n\n🔑 **Aapka Unique Invite Code:** `{unique_code}`\n\nIse apne doston ke sath share karein!")
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
