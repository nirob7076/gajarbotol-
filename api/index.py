from flask import Flask, request, abort
import telebot
from bot_instance import bot
import main
import admin

app = Flask(__name__)

main.register_user_handlers()
admin.register_admin_handlers()

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
    return "Bot is successfully running on Vercel with MySQL!", 200
