import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'BloodMushroomBot')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 8080))

application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "Player"
    
    # Используем обычную URL кнопку вместо web_app
    keyboard = [[InlineKeyboardButton(
        "🎮 Играть в Blood Mushroom", 
        url=f"https://t.me/{BOT_USERNAME}/app"
    )]]
    
    await update.message.reply_text(
        f"🍄 *Добро пожаловать в Blood Mushroom, {first_name}!*\n\n"
        f"🎮 Нажмите кнопку ниже, чтобы начать играть\n"
        f"💰 Фармите грибы, собирайте эссенцию и зарабатывайте TON!\n\n"
        f"Удачи! 🚀",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info(f"User {user_id} started bot")

async def webhook_handler(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text='OK')

async def health_check(request):
    return web.Response(text='OK')

async def setup_webhook(app):
    global application
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    await application.initialize()
    await application.start()
    
    webhook_url = f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}"
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message"],
        drop_pending_updates=True
    )
    
    logger.info(f"✅ Webhook set to {webhook_url}")

async def cleanup_webhook(app):
    if application:
        await application.stop()
        await application.shutdown()
    logger.info("🛑 Bot stopped")

def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    if not WEBHOOK_URL:
        logger.error("❌ WEBHOOK_URL not set!")
        return
    
    logger.info("🤖 Starting Blood Mushroom Bot (webhook mode)...")
    
    app = web.Application()
    app.router.add_post(f'/webhook/{TELEGRAM_TOKEN}', webhook_handler)
    app.router.add_get('/health', health_check)
    
    app.on_startup.append(setup_webhook)
    app.on_cleanup.append(cleanup_webhook)
    
    logger.info(f"✅ Bot is running on port {PORT}")
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
