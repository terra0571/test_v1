import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
PORT = int(os.environ.get('PORT', 8443))
APP_NAME = os.getenv('APP_NAME')

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"Salom {user.first_name}!\nSizning ID: {user.id}")

def main():
    logger.info("Bot ishga tushmoqda...")
    updater = Updater(TOKEN, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    try:
        logger.info(f"Webhook sozlanmoqda: https://{APP_NAME}.herokuapp.com/{TOKEN}")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}"
        )
        logger.info("Bot muvaffaqiyatli ishga tushdi!")
        updater.idle()
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")

if __name__ == '__main__':
    main()
