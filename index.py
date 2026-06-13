from flask import Flask, request, abort
import telebot
from bot_instance import bot
import main

app = Flask(__name__)

# ইউজার হ্যান্ডলার চালু করা
main.register_user_handlers()

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        else:
            abort(403)
    return "Bot is running perfectly on Vercel without database!", 200
