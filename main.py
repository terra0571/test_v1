import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot tokenini environment o'zgaruvchisidan olamiz
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8443))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Log konfiguratsiyasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clean_text(text):
    """Matndan maxsus belgilarni tozalash"""
    return text.replace('\n', ' ').replace('\r', ' ').replace('\\', '') if text else ""

def start(update: Update, context: CallbackContext) -> None:
    """Start command handler"""
    user = update.effective_user
    update.message.reply_text(
        f"👋 Salom {clean_text(user.first_name)}!\n"
        f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
        "🔍 ID aniqlash uchun:\n"
        "• Foydalanuvchi xabarini forward qiling\n"
        "• Kanal/guruh linkini yuboring\n"
        "• Username yuboring (@username)\n"
        "• Xabarga reply qilib /id yozing",
        parse_mode='HTML'
    )

def handle_message(update: Update, context: CallbackContext) -> None:
    """Barcha xabarlarni qayta ishlash"""
    message = update.message
    
    # Forward qilingan xabar
    if message.forward_from:
        user = message.forward_from
        update.message.reply_text(
            "📤 Forward qilingan foydalanuvchi:\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"👤 Ism: {clean_text(user.full_name)}\n"
            f"📌 Username: @{user.username if user.username else 'yoq'}",
            parse_mode='HTML'
        )
        return
    
    # Reply qilingan xabar
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        update.message.reply_text(
            "↩️ Reply qilingan foydalanuvchi:\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"👤 Ism: {clean_text(user.full_name)}\n"
            f"📌 Username: @{user.username if user.username else 'yoq'}",
            parse_mode='HTML'
        )
        return
    
    # Kanal havolasi
    if message.text and message.text.startswith(("https://t.me/", "t.me/")):
        username = message.text.split("/")[-1]
        update.message.reply_text(
            f"🔗 Kanal/guruh havolasi:\n{message.text}\n"
            f"📌 Username: @{username}\n\n"
            "🆔 ID ni olish uchun:\n"
            "1. Botni ushbu kanal/guruhga qo'shing\n"
            "2. Guruhda /id buyrug'ini yuboring"
        )
        return
    
    # Username
    if message.text and message.text.startswith("@"):
        update.message.reply_text(
            f"📌 Username: {message.text}\n\n"
            "🆔 ID ni olish uchun:\n"
            "1. U sizga xabar yuborsa\n"
            "2. Xabarini forward qiling\n"
            "3. Xabariga reply qilib /id yozing"
        )
        return
    
    # Boshqa xabarlarga javob
    update.message.reply_text(
        "ℹ️ ID aniqlash uchun quyidagilardan birini yuboring:\n\n"
        "• Kanal/guruh havolasi (masalan: https://t.me/channel)\n"
        "• Foydalanuvchi username (@username)\n"
        "• Forward qilingan xabar\n"
        "• Reply qilingan xabar\n\n"
        "Yoki /start buyrug'ini yuboring"
    )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Xatoliklarni log qilish"""
    logger.error(msg="Xatolik yuz berdi:", exc_info=context.error)

def main():
    """Botni ishga tushirish"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("id", start))

    # Message handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Error handler
    dispatcher.add_error_handler(error_handler)

    # Railway production muhiti
    if WEBHOOK_URL:
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
        logger.info(f"Webhook orqali ishga tushirildi: {WEBHOOK_URL}")
    else:
        # Lokal ishlash uchun polling
        updater.start_polling()
        logger.info("Polling rejimida ishga tushdi...")

    updater.idle()

if __name__ == '__main__':
    main()
