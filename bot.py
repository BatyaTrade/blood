import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'BloodMushroomBot')  # Имя бота без @

# Команда /start (только приветствие + кнопка WebApp)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "Player"
    
    # Создаём кнопку для запуска WebApp
    keyboard = [
        [InlineKeyboardButton(
            "🎮 Играть в Blood Mushroom", 
            web_app={"url": f"https://t.me/{BOT_USERNAME}/app"}
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🍄 *Добро пожаловать в Blood Mushroom, {first_name}!*\n\n"
        f"🎮 Нажмите кнопку ниже, чтобы начать играть\n"
        f"💰 Фармите грибы, собирайте эссенцию и зарабатывайте TON!\n\n"
        f"Удачи! 🚀",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"User {user_id} started bot")

# Главная функция
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    logger.info("🤖 Starting Blood Mushroom Bot...")
    
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Только команда /start
    app.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Bot is running (polling mode)")
    
    # Запускаем бота
    app.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
