import base64
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot, ADMIN_ID
from database import get_connection

# ইউজার আইডিকে রেফার কোডে বানানোর ফাংশন
def encode_ref_code(user_id):
    return base64.urlsafe_b64encode(str(user_id).encode()).decode().rstrip('=')

# রেফার কোড থেকে ইউজার আইডি বের করার ফাংশন
def decode_ref_code(code):
    try:
        padding_needed = len(code) % 4
        if padding_needed:
            code += '=' * (4 - padding_needed)
        return int(base64.urlsafe_b64decode(code).decode())
    except:
        return None

def register_user_handlers():
    
    def check_sub(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT channel_username FROM channels")
        channels = cursor.fetchall()
        conn.close()
        
        if not channels:
            return True 

        for ch in channels:
            try:
                status = bot.get_chat_member(ch['channel_username'], user_id).status
                if status not in ['member', 'administrator', 'creator']:
                    return False
            except:
                return False
        return True

    @bot.message_handler(commands=['start'])
    def start_command(message):
        user_id = message.from_user.id
        
        ref_id = None
        args = message.text.split()
        if len(args) > 1:
            # রেফার কোড ডিকোড করে আসল ইউজার আইডি বের করা
            decoded_id = decode_ref_code(args[1])
            if decoded_id and decoded_id != user_id:
                ref_id = decoded_id
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # নতুন ইউজার সেভ করা
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (%s, %s)", (user_id, ref_id))
            
        # চ্যানেল জয়েন চেক (একই লাইনে বাটন)
        if not check_sub(user_id):
            cursor.execute("SELECT channel_username FROM channels LIMIT 1")
            ch = cursor.fetchone()
            channel_link = f"https://t.me/{ch['channel_username'].replace('@', '')}" if ch else ""
            
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📢 জয়েন চ্যানেল", url=channel_link),
                InlineKeyboardButton("✅ চেক", callback_data="check_join")
            )
            bot.send_message(user_id, "⚠️ **বটটি ব্যবহার করতে আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে!**\n\nনিচের বাটন থেকে জয়েন করে 'চেক' বাটনে ক্লিক করুন।", reply_markup=markup, parse_mode="Markdown")
            conn.close()
            return
            
        conn.close()
        show_main_menu(message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "check_join")
    def check_join_callback(call):
        user_id = call.from_user.id
        if check_sub(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, "🎉 ধন্যবাদ! আপনি সফলভাবে জয়েন করেছেন।", show_alert=False)
            
            # রেফারেল বোনাস অ্যাড করা
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT referred_by, bonus_received FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data['referred_by'] and not user_data['bonus_received']:
                ref_id = user_data['referred_by']
                
                cursor.execute("SELECT ref_bonus FROM settings WHERE id = 1")
                bonus = cursor.fetchone()['ref_bonus']
                
                # রেফারের ব্যালেন্স বাড়ানো
                cursor.execute("UPDATE users SET balance = balance + %s, total_refs = total_refs + 1 WHERE user_id = %s", (bonus, ref_id))
                cursor.execute("UPDATE users SET bonus_received = TRUE WHERE user_id = %s", (user_id,))
                
                try:
                    bot.send_message(ref_id, f"🎉 **নতুন রেফার!**\nআপনার রেফারে একজন জয়েন করেছে। আপনি পেয়েছেন {bonus}৳", parse_mode="Markdown")
                except: pass
                
            conn.close()
            show_main_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন করেননি!", show_alert=True)

    def show_main_menu(chat_id):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🎁 রেফার করুন"), 
            KeyboardButton("💰 ব্যালেন্স চেক")
        )
        markup.add(
            KeyboardButton("💳 উইড্র"), 
            KeyboardButton("📊 স্ট্যাটাস")
        )
        bot.send_message(chat_id, "🏠 **মেনু থেকে আপনার প্রয়োজনীয় বাটনটি বেছে নিন:**", reply_markup=markup, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text == "🎁 রেফার করুন")
    def refer_btn(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ref_bonus FROM settings WHERE id = 1")
        bonus = cursor.fetchone()['ref_bonus']
        conn.close()
        
        # এখানে ইউজারের আইডির বদলে সিক্রেট কোড জেনারেট করা হচ্ছে
        ref_code = encode_ref_code(message.from_user.id)
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"
        
        bot.send_message(message.chat.id, f"🔗 **আপনার রেফার লিংক:**\n`{ref_link}`\n\n💡 প্রতি রেফারে আপনি পাবেন **{bonus}৳**", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text == "💰 ব্যালেন্স চেক")
    def balance_btn(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (message.from_user.id,))
        user = cursor.fetchone()
        conn.close()
        
        bal = user['balance'] if user else 0
        bot.send_message(message.chat.id, f"💳 **আপনার বর্তমান ব্যালেন্স:** {bal}৳", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text == "💳 উইড্র")
    def withdraw_btn(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (message.from_user.id,))
        user = cursor.fetchone()
        
        cursor.execute("SELECT min_withdraw FROM settings WHERE id = 1")
        min_withdraw = cursor.fetchone()['min_withdraw']
        conn.close()
        
        if user and user['balance'] >= min_withdraw:
            msg = bot.send_message(message.chat.id, "📝 উইড্র করতে আপনার **বিকাশ/নগদ নাম্বার** এবং **অ্যামাউন্ট** লিখে পাঠান।\n(উদাহরণ: ০১৯xxxxxx বিকাশ ৫০)", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_withdraw)
        else:
            bot.send_message(message.chat.id, f"⚠️ উইড্র করতে আপনার অন্তত **{min_withdraw}৳** প্রয়োজন।", parse_mode="Markdown")

    def process_withdraw(message):
        user_id = message.from_user.id
        details = message.text
        bot.send_message(ADMIN_ID, f"🔔 **নতুন উইড্র রিকোয়েস্ট!**\n\n👤 ইউজার আইডি: `{user_id}`\n📝 ডিটেইলস: {details}", parse_mode="Markdown")
        bot.send_message(user_id, "✅ **আপনার উইড্র রিকোয়েস্ট সফলভাবে অ্যাডমিনের কাছে পাঠানো হয়েছে।**", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text == "📊 স্ট্যাটাস")
    def status_btn(message):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT total_refs FROM users WHERE user_id = %s", (message.from_user.id,))
        user = cursor.fetchone()
        conn.close()
        
        total_refs = user['total_refs'] if user else 0
        bot.send_message(message.chat.id, f"📊 **আপনার একাউন্ট স্ট্যাটাস:**\n\n👥 মোট রেফার করেছেন: **{total_refs} জন**", parse_mode="Markdown")