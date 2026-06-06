import os
import logging
import re
import cv2
import pytesseract
import numpy as np
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# --- ការកំណត់ Environment ---
BOT_TOKEN = os.getenv('8726446573:AAGlSh4ZrIOJIeeP53CS8O27AIJqSgIxai8')
BOT_USERNAME = 'autosenderBaggage_phone_bot'
GROUP_CHAT_ID = '-5116254772'

PORT = int(os.environ.get('PORT', '8080'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- មុខងាររបស់ Bot ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    nparr = np.frombuffer(photo_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    await update.message.reply_text("🔎 កំពុងចាប់យកលេខទូរស័ព្ទ...")

    # ប្រើ Pytesseract ជំនួស EasyOCR
    raw_text = pytesseract.image_to_string(image)
    cleaned_text = re.sub(r'\D', '', raw_text)
    phone_match = re.search(r'\d{9,10}', cleaned_text)

    if phone_match:
        detected_phone = phone_match.group()
        customer_bot_link = f"https://t.me/{BOT_USERNAME}?start={detected_phone}"
        formatted_phone = "855" + detected_phone[1:] if detected_phone.startswith('0') else detected_phone
        direct_chat_link = f"https://t.me/+{formatted_phone}"

        keyboard = [
            [InlineKeyboardButton("💬 បើក Chat ជាមួយគាត់", url=direct_chat_link)],
            [InlineKeyboardButton("🔗 ចម្លង Link ផ្ញើឱ្យគាត់", url=f"https://t.me/share/url?url={customer_bot_link}&text=សូមចុច Link នេះរួចផ្ញើទីតាំងឱ្យខ្ញុំផង")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"📦 **មានឥវ៉ាន់ថ្មី!**\n📱 លេខទូរស័ព្ទលើប្រអប់៖ `{detected_phone}`\n\nសូមប្រើប៊ូតុងខាងក្រោមដើម្បីទាក់ទងទៅគាត់៖",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"✅ រកឃើញលេខ {detected_phone} និងបានបញ្ជូនទៅ Group។")
    else:
        await update.message.reply_text("❌ រកមិនឃើញលេខទូរស័ព្ទទេ។")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        expected_phone = context.args[0]
        context.user_data['expected_phone'] = expected_phone
        keyboard = [[KeyboardButton("🔐 ចុចទីនេះដើម្បីផ្ទៀងផ្ទាត់លេខទូរស័ព្ទ", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("សូមចុចប៊ូតុងខាងក្រោមដើម្បីផ្ទៀងផ្ទាត់លេខទូរស័ព្ទ Telegram របស់អ្នក៖", reply_markup=reply_markup)
    else:
        await update.message.reply_text("សូមស្វាគមន៍! Bot នេះប្រើសម្រាប់តែទទួលទីតាំងដឹកឥវ៉ាន់ប៉ុណ្ណោះ។")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    expected_phone = context.user_data.get('expected_phone')
    if contact and expected_phone:
        user_phone = re.sub(r'\D', '', contact.phone_number)
        formatted_expected = "855" + expected_phone[1:] if expected_phone.startswith('0') else expected_phone
        formatted_expected = re.sub(r'\D', '', formatted_expected)
        if user_phone == formatted_expected:
            keyboard = [[KeyboardButton("📍 ចុចទីនេះដើម្បីផ្ញើទីតាំង", request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("✅ ការផ្ទៀងផ្ទាត់ជោគជ័យ! សូមចុចប៊ូតុងខាងក្រោមដើម្បីផ្ញើទីតាំង៖", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ ការផ្ទៀងផ្ទាត់បរាជ័យ!", reply_markup=ReplyKeyboardRemove())

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    expected_phone = context.user_data.get('expected_phone', 'មិនស្គាល់លេខ')
    if location:
        maps_url = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"📍 **ទីតាំងពី៖** {expected_phone}\n🔗 {maps_url}")
        await update.message.reply_text("🙏 អរគុណច្រើន!", reply_markup=ReplyKeyboardRemove())

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("កំហុស៖ សូមដាក់ BOT_TOKEN ក្នុង Environment Variables!")
    elif not WEBHOOK_URL:
        print("កំហុស៖ សូមដាក់ WEBHOOK_URL ក្នុង Environment Variables!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        app.add_handler(MessageHandler(filters.LOCATION, handle_location))
        
        print(f"🚀 Bot កំពុងដំណើរការលើ Port {PORT}...")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL
        )
