# Blood Mushroom Telegram Bot

Telegram бот для игры Blood Mushroom, развернутый на Fly.io.

## 🚀 Быстрый старт

### 1. Установка Fly CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Авторизация

```bash
fly auth login
```

### 3. Инициализация приложения

```bash
cd telegram-bot
fly launch
```

Ответь на вопросы:
- **App name**: `blood-mushroom-bot` (или своё уникальное имя)
- **Region**: `ams` (Amsterdam) или `fra` (Frankfurt)
- **PostgreSQL**: `No` (используем существующую БД)
- **Deploy now**: `No`

### 4. Установка секретов

```bash
fly secrets set TELEGRAM_BOT_TOKEN="ваш_токен_от_BotFather"
fly secrets set DATABASE_URL="postgresql://user:pass@host/db"
fly secrets set ADMIN_TELEGRAM_ID="ваш_telegram_id"
```

### 5. Деплой

```bash
fly deploy
```

### 6. Проверка статуса

```bash
fly status
fly logs
```

## 📋 Команды бота

- `/start` - Начать работу с ботом
- `/stats` - Показать статистику игрока
- `/broadcast <сообщение>` - Рассылка сообщений (только для админа)

## 🔧 Полезные команды Fly.io

```bash
# Просмотр логов в реальном времени
fly logs -f

# Перезапуск
fly apps restart blood-mushroom-bot

# Масштабирование
fly scale vm shared-cpu-1x --memory 512

# SSH доступ к контейнеру
fly ssh console

# Остановка/запуск
fly apps pause blood-mushroom-bot
fly apps resume blood-mushroom-bot
```

## 🔐 Переменные окружения

- `TELEGRAM_BOT_TOKEN` - Токен бота от BotFather
- `DATABASE_URL` - URL подключения к PostgreSQL
- `ADMIN_TELEGRAM_ID` - Telegram ID администратора

## 📝 Настройка menu button в BotFather

1. Открой [@BotFather](https://t.me/BotFather)
2. `/setmenubutton`
3. Выбери своего бота
4. Отправь текст кнопки: `🎮 Играть`
5. Отправь URL: `https://t.me/BloodMushroomBot/app`

## 🎯 Структура проекта

```
telegram-bot/
├── bot.py              # Основной код бота
├── requirements.txt    # Зависимости Python
├── Dockerfile          # Контейнер для деплоя
├── fly.toml           # Конфигурация Fly.io
├── .gitignore         # Игнорируемые файлы
└── README.md          # Документация
```

