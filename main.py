import os
import json
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

DATA_FILE = "users.json"

# File se data load karna
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# File me data save karna
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

users_db = load_data()

TASKS_DB = [
    {"id": 1, "title": "Join Telegram Channel", "reward": 10, "url": "https://t.me/your_channel"},
    {"id": 2, "title": "Visit YouTube Video", "reward": 15, "url": "https://youtube.com"},
    {"id": 3, "title": "Join Sponsor Group", "reward": 10, "url": "https://t.me/your_channel"}
]

MASTER_CODES = ["TASK2026", "ADMIN123"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id in users_db:
        show_main_menu(message)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Enter Invite Code", callback_data="ask_code"))
        
        bot.send_message(
            message.chat.id, 
            "Welcome to Task Bot!\n\nIs exclusive platform par aane ke liye aapko ek valid Invite Code ki zaroorat hai.\n\nNeeche diye gaye button par click karke code darj karein:", 
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "ask_code")
def callback_query(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Kripya apna valid Invite Code abhi yahan message me bhejiye:")
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
            "balance": 10.0,
            "my_code": unique_code,
            "completed_tasks": []
        }
        save_data(users_db)  # Data permanently save ho raha hai
        
        bot.send_message(
            message.chat.id, 
            f"Badhai ho {user_name}!\n\nAapka invite code verify ho gaya hai aur 10 points signup bonus mil chuka hai.\n\nAapka Unique Code: {unique_code}"
        )
        show_main_menu(message)
    else:
        msg = bot.reply_to(message, "Galat Invite Code! Kripya sahi code dobara bhejiye:")
        bot.register_next_step_handler(msg, verify_invite_code)

def show_main_menu(message):
    chat_id = message.chat.id if hasattr(message, 'chat') else message['chat']['id']
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Wallet", callback_data="wallet"),
        InlineKeyboardButton("24/7 Tasks", callback_data="view_tasks")
    )
    markup.row(
        InlineKeyboardButton("Daily Bonus", callback_data="daily_bonus"),
        InlineKeyboardButton("Referral Code", callback_data="referral")
    )
    
    bot.send_message(
        chat_id,
        "Main Menu:\n\nNeeche diye gaye options me se chunein:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_menu_clicks(call):
    user_id = str(call.from_user.id)
    bot.answer_callback_query(call.id)
    
    if user_id not in users_db:
        bot.send_message(call.message.chat.id, "Pehle /start command ka use karke apna account activate karein.")
        return

    if call.data == "wallet":
        bal = users_db[user_id]["balance"]
        bot.send_message(call.message.chat.id, f"Aapka Current Balance: {bal} Points")
        
    elif call.data == "view_tasks":
        markup = InlineKeyboardMarkup()
        for task in TASKS_DB:
            if task["id"] not in users_db[user_id]["completed_tasks"]:
                markup.add(InlineKeyboardButton(f"{task['title']} (+{task['reward']}Pts)", url=task["url"]))
                markup.add(InlineKeyboardButton(f"Claim Reward (Task {task['id']})", callback_data=f"claim_{task['id']}"))
        
        if len(markup.keyboard) == 0:
            bot.send_message(call.message.chat.id, "Abhi ke liye saare tasks poore ho chuke hain. Naye tasks jald aayenge!")
        else:
            bot.send_message(call.message.chat.id, "Available 24/7 Tasks:\n\nPehle link par click karke task poora karein, fir neeche claim button dabayein:", reply_markup=markup)
            
    elif call.data.startswith("claim_"):
        task_id = int(call.data.split("_")[1])
        if task_id not in users_db[user_id]["completed_tasks"]:
            task = next((t for t in TASKS_DB if t["id"] == task_id), None)
            if task:
                users_db[user_id]["balance"] += task["reward"]
                users_db[user_id]["completed_tasks"].append(task_id)
                save_data(users_db)  # Balance update hone par file me save hoga
                bot.send_message(call.message.chat.id, f"Badhai ho! Aapke account me {task['reward']} points add kar diye gaye hain.")
        else:
            bot.send_message(call.message.chat.id, "Aap yeh task pehle hi claim kar chuke hain!")
            
    elif call.data == "daily_bonus":
        users_db[user_id]["balance"] += 5.0
        save_data(users_db)  # Bonus milne par file me save hoga
        bot.send_message(call.message.chat.id, "Aapko aaj ka 5 points Daily Bonus mil gaya hai!")
        
    elif call.data == "referral":
        code = users_db[user_id]["my_code"]
        bot.send_message(call.message.chat.id, f"Aapka Referral Code: {code}\n\nIse doston ke sath share karein!")

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run)
    t.start()
    
    bot.remove_webhook()
    bot.infinity_polling()
