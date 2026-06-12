from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot, ADMIN_ID
from database import get_connection

def register_admin_handlers():
    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.from_user.id != ADMIN_ID:
            return 
            
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("💸 Set Ref Bonus", callback_data="admin_bonus"),
            InlineKeyboardButton("🏦 Set Min Withdraw", callback_data="admin_withdraw")
        )
        markup.add(
            InlineKeyboardButton("📢 Add Channel", callback_data="admin_channel"),
            InlineKeyboardButton("👥 Total Users", callback_data="admin_users")
        )
        bot.send_message(message.chat.id, "👨‍💻 **অ্যাডমিন প্যানেলে স্বাগতম!**", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
    def admin_callbacks(call):
        if call.from_user.id != ADMIN_ID:
            return
            
        if call.data == "admin_users":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total = cursor.fetchone()['total']
            conn.close()
            bot.answer_callback_query(call.id, f"মোট ইউজার: {total} জন", show_alert=True)
            
        elif call.data == "admin_bonus":
            msg = bot.send_message(call.message.chat.id, "নতুন রেফার বোনাস অ্যামাউন্ট লিখুন:")
            bot.register_next_step_handler(msg, update_bonus)
            
        elif call.data == "admin_withdraw":
            msg = bot.send_message(call.message.chat.id, "নতুন মিনিমাম উইড্র অ্যামাউন্ট লিখুন:")
            bot.register_next_step_handler(msg, update_withdraw)
            
        elif call.data == "admin_channel":
            msg = bot.send_message(call.message.chat.id, "নতুন চ্যানেলের ইউজারনেম দিন (যেমন: @MyChannel):")
            bot.register_next_step_handler(msg, add_channel)

    def update_bonus(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET ref_bonus = %s WHERE id = 1", (int(message.text),))
        conn.close()
        bot.send_message(message.chat.id, "✅ রেফার বোনাস আপডেট হয়েছে!")

    def update_withdraw(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET min_withdraw = %s WHERE id = 1", (int(message.text),))
        conn.close()
        bot.send_message(message.chat.id, "✅ মিনিমাম উইড্র আপডেট হয়েছে!")

    def add_channel(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels") # আগের চ্যানেল ডিলিট করে নতুনটি রাখবে (যেহেতু আপনি বলেছেন ১টি চ্যানেল থাকবে)
        cursor.execute("INSERT INTO channels (channel_username) VALUES (%s)", (message.text,))
        conn.close()
        bot.send_message(message.chat.id, f"✅ নতুন চ্যানেল ({message.text}) অ্যাড করা হয়েছে!")