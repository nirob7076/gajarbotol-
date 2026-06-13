from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_instance import bot
from datetime import datetime, timedelta

def register_user_handlers():
    
    @bot.message_handler(commands=['start'])
    def start_command(message):
        # ইউজারের ফার্স্ট নেম নেওয়া
        user_name = message.from_user.first_name
        
        # সুন্দর ওয়েলকাম মেসেজ
        welcome_text = (
            f"হ্যালো *{user_name}*! 👋\n\n"
            "আমাদের টেলিগ্রাম বটে আপনাকে স্বাগতম। 🎉\n"
            "এটি একটি সিম্পল বট যা আপনাকে বাংলাদেশের বর্তমান সঠিক সময় জানাতে পারে।\n\n"
            "👇 *নিচের বাটনে ক্লিক করে বর্তমান সময়টি দেখে নিন!*"
        )
        
        # ইনলাইন বাটন তৈরি
        markup = InlineKeyboardMarkup()
        time_btn = InlineKeyboardButton("🕒 বর্তমান সময় দেখুন", callback_data="show_time")
        markup.add(time_btn)
        
        # মেসেজ সেন্ড করা
        bot.send_message(
            message.chat.id, 
            welcome_text, 
            reply_markup=markup, 
            parse_mode="Markdown"
        )

    # ইনলাইন বাটনে ক্লিক করলে যা হবে
    @bot.callback_query_handler(func=lambda call: call.data == "show_time")
    def time_callback(call):
        # Vercel সার্ভার UTC টাইমে থাকে, তাই বাংলাদেশের সময় (+6 ঘণ্টা) বের করা হচ্ছে
        bd_time = datetime.utcnow() + timedelta(hours=6)
        
        # সময় সুন্দরভাবে সাজানো (যেমন: 09:35:12 AM - 13 June, 2026)
        formatted_time = bd_time.strftime("%I:%M:%S %p \n📅 %d %B, %Y")
        
        # স্ক্রিনে পপ-আপ অ্যালার্ট (Alert) হিসেবে সময় দেখানো
        bot.answer_callback_query(
            call.id, 
            f"🕒 বাংলাদেশের বর্তমান সময়:\n\n{formatted_time}", 
            show_alert=True
        )
