import os
import asyncio
import logging
import psycopg2
from datetime import datetime
from telegram import Bot, Update
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

# Подключение к PostgreSQL
def get_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Player"
    
    logger.info(f"User {user_id} ({username}) started bot")
    
    # Сохраняем/обновляем пользователя в БД
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO users (telegram_id, username, last_active) 
                   VALUES (%s, %s, NOW())
                   ON CONFLICT (telegram_id) DO UPDATE 
                   SET last_active = NOW()""",
                (user_id, username)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"DB error: {e}")
    
    await update.message.reply_text(
        f"🍄 *Добро пожаловать в Blood Mushroom, {username}!*\n\n"
        f"🎮 Запустите игру через кнопку меню внизу\n"
        f"💰 Фармите эссенцию и зарабатывайте TON!\n\n"
        f"🔔 Включите уведомления, чтобы не пропустить важные события!",
        parse_mode='Markdown'
    )

# Команда /stats (для пользователя)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    conn = get_db()
    if not conn:
        await update.message.reply_text("⚠️ Ошибка подключения к базе данных")
        return
    
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT blood_balance, essence_balance, task_token_balance 
               FROM users WHERE telegram_id = %s""",
            (user_id,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            blood, essence, tokens = result
            await update.message.reply_text(
                f"📊 *Ваша статистика:*\n\n"
                f"🩸 Кровь: {blood:,.2f}\n"
                f"💧 Эссенция: {essence:,.4f}\n"
                f"🎟️ Токены: {tokens}\n\n"
                f"Продолжайте фармить! 🍄",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❓ Вы ещё не зарегистрированы в игре.\n"
                "Откройте приложение через меню бота."
            )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text("⚠️ Ошибка получения статистики")

# Команда /broadcast (только для админа)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет прав для этой команды")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 *Использование:*\n"
            "`/broadcast <сообщение>`\n\n"
            "Отправит сообщение всем пользователям",
            parse_mode='Markdown'
        )
        return
    
    message = " ".join(context.args)
    
    conn = get_db()
    if not conn:
        await update.message.reply_text("⚠️ Ошибка подключения к БД")
        return
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT telegram_id FROM users WHERE telegram_id IS NOT NULL")
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        sent = 0
        failed = 0
        
        await update.message.reply_text(f"📤 Отправка {len(users)} пользователям...")
        
        for (uid,) in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📢 *Уведомление от Blood Mushroom*\n\n{message}",
                    parse_mode='Markdown'
                )
                sent += 1
                await asyncio.sleep(0.05)  # Защита от rate limit
            except Exception as e:
                logger.warning(f"Failed to send to {uid}: {e}")
                failed += 1
        
        await update.message.reply_text(
            f"✅ Отправлено: {sent}\n"
            f"❌ Ошибок: {failed}"
        )
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await update.message.reply_text("⚠️ Ошибка рассылки")

# Отправка уведомлений по расписанию
async def scheduled_notifications(app):
    """Пример периодических уведомлений"""
    while True:
        await asyncio.sleep(3600)  # Каждый час
        
        conn = get_db()
        if not conn:
            continue
        
        try:
            cur = conn.cursor()
            # Найти пользователей с накопленной эссенцией
            cur.execute(
                """SELECT u.telegram_id, SUM(m.base_income_ph) as total_income
                   FROM users u
                   JOIN mushrooms m ON m.user_id = u.telegram_id
                   WHERE u.last_active > NOW() - INTERVAL '7 days'
                   GROUP BY u.telegram_id
                   HAVING SUM(m.base_income_ph) > 0"""
            )
            users = cur.fetchall()
            cur.close()
            conn.close()
            
            for uid, income in users:
                try:
                    await app.bot.send_message(
                        chat_id=uid,
                        text=f"🍄 Ваши грибы накопили эссенцию!\n\n"
                             f"💧 Доход: {income:.4f} Эс/час\n"
                             f"Соберите урожай в игре! 🎁"
                    )
                    await asyncio.sleep(0.1)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Scheduled notification error: {e}")

# Главная функция
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    logger.info("🤖 Starting Blood Mushroom Bot...")
    
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # Запускаем фоновые задачи
    asyncio.create_task(scheduled_notifications(app))
    
    # Запускаем бота
    logger.info("✅ Bot is running (polling mode)")
    app.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()

