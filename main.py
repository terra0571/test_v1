import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot tokenini environmentdan olamiz
TOKEN = os.getenv('TELEGRAM_TOKEN')
PORT = int(os.environ.get('PORT', 8443))

# Log konfiguratsiyasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f"Salom {user.first_name}!\n"
        f"Sizning ID: {user.id}\n\n"
        "ID aniqlash uchun:\n"
        "- Foydalanuvchi xabarini forward qiling\n"
        "- Kanal/guruh linkini yuboring\n"
        "- Username yuboring (@username)"
    )

def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    
    if message.forward_from:
        user = message.forward_from
        update.message.reply_text(
            f"Forward qilingan foydalanuvchi:\n"
            f"ID: {user.id}\n"
            f"Ism: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'yoq'}"
        )
        return
    
    if message.text and message.text.startswith(("https://t.me/", "t.me/")):
        username = message.text.split("/")[-1]
        update.message.reply_text(f"Kanal username: @{username}")
        return
        
    if message.text and message.text.startswith("@"):
        update.message.reply_text(f"Username: {message.text}")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("id", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Heroku uchun webhook sozlash
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://your-app-name.herokuapp.com/{TOKEN}"
    )
    updater.idle()

if __name__ == '__main__':
    main()
