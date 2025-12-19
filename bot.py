import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID', '0'))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Player"
    
    logger.info(f"User {user_id} ({username}) started bot")
    
    await update.message.reply_text(
        f"🍄 *Добро пожаловать в Blood Mushroom, {username}!*\n\n"
        f"🎮 Запустите игру через кнопку меню внизу\n"
        f"💰 Фармите эссенцию и зарабатывайте TON!\n\n"
        f"Команды:\n"
        f"/stats - Ваша статистика\n"
        f"/help - Помощь",
        parse_mode='Markdown'
    )

# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Player"
    
    await update.message.reply_text(
        f"📊 *Статистика {username}*\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"🩸 Кровь: 0\n"
        f"💧 Эссенция: 0\n"
        f"🎟️ Токены: 0\n\n"
        f"_Подключение к БД будет добавлено позже_",
        parse_mode='Markdown'
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка Blood Mushroom Bot*\n\n"
        "🍄 *Доступные команды:*\n"
        "/start - Запустить бота\n"
        "/stats - Показать статистику\n"
        "/help - Эта справка\n\n"
        "🎮 Играйте через меню бота!",
        parse_mode='Markdown'
    )

# Главная функция
def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    logger.info("🤖 Starting Blood Mushroom Bot...")
    
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    logger.info("✅ Bot is running (polling mode)")
    
    # Запускаем бота
    app.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
