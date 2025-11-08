# GuideFarm Bot - Восстановленная версия для bolt.new

## Статус: ГОТОВ К ЗАПУСКУ

Проект полностью восстановлен и адаптирован для работы в bolt.new с поддержкой Telegram Mini App.

---

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопируйте шаблон
cp .env.example .env

# Откройте .env и добавьте ваши ключи
nano .env
```

**Минимум нужно:**
- `TELEGRAM_BOT_TOKEN` (от @BotFather)
- `GEMINI_API_KEY` (бесплатно на ai.google.dev)

### 3. Запуск

```bash
python main.py
```

Или:

```bash
./start.sh
```

---

## Что было сделано

### Восстановлена структура проекта

```
project/
  src/
    bot/
      handlers.py       # Telegram бот с поддержкой Web App
    core/
      config.py         # Управление настройками
      meta_guardian.py  # Упрощенный мониторинг

  webapp/
    index.html          # Telegram Mini App интерфейс
    server.py           # Flask сервер для Web App

  main.py               # Точка входа
  requirements.txt      # Минимальные зависимости
  .env.example          # Шаблон настроек
```

### Добавлено

1. **Telegram Mini App** - веб-панель управления ботом
   - Статус системы в реальном времени
   - Отправка команд боту через веб-интерфейс
   - Просмотр логов активности
   - Стильный дизайн в зеленых тонах (DOBRO)

2. **Команды бота**
   - `/start` - Приветствие
   - `/help` - Справка
   - `/panel` - Открыть Web App панель
   - `/status` - Проверить статус систем

3. **Web App Server** - Flask сервер для раздачи mini app

### Упрощено

- Убраны сложные зависимости (WeasyPrint, PDF генерация)
- Удалены неиспользуемые модули (AI writer, designer, ozon)
- Оставлен минимальный рабочий функционал

### Адаптировано для bolt.new

- Polling mode по умолчанию (проще для разработки)
- Автоматическое определение режима работы
- Graceful handling конфликтующих инстансов
- Поддержка переменных окружения

---

## Telegram Mini App

### Как работает

1. Пользователь отправляет `/panel` в боте
2. Бот показывает кнопку "Открыть панель управления"
3. При нажатии открывается веб-интерфейс внутри Telegram
4. Через панель можно:
   - Видеть статус бота
   - Отправлять команды
   - Смотреть логи

### Настройка для production

После деплоя на Railway/Render:

1. Получите URL вашего приложения (например: `https://your-app.railway.app`)
2. Обновите `WEBAPP_URL` в .env:
   ```
   WEBAPP_URL=https://your-app.railway.app/webapp
   ```
3. Перезапустите бота

### Файлы Web App

- `webapp/index.html` - Основной интерфейс
- `webapp/server.py` - Flask сервер (можно запустить отдельно)

---

## Деплой на Railway

1. Создайте аккаунт на https://railway.app
2. Создайте новый проект из GitHub
3. Добавьте переменные окружения из .env
4. Railway автоматически установит зависимости и запустит бота

**Start Command:** `python main.py`

---

## Деплой на Render

1. Создайте аккаунт на https://render.com
2. Создайте Web Service
3. Укажите:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Добавьте переменные окружения
5. Deploy

---

## Файлы из Replit (удалены/заменены)

Следующие файлы были специфичны для Replit и больше не нужны:

- `.replit` - конфигурация Replit IDE (заменен на start.sh)
- `replit.nix` - пакетный менеджер Replit (не нужен)
- File lock механизм - упрощен для bolt.new

---

## Переменные окружения

### Обязательные

```bash
TELEGRAM_BOT_TOKEN=your_token    # От @BotFather
GEMINI_API_KEY=your_key          # Или другой AI provider
```

### Опциональные

```bash
OPENAI_API_KEY=your_key          # Альтернативный AI
XAI_API_KEY=your_key             # Еще один AI
OZON_CLIENT_ID=your_id           # Для Ozon интеграции
OZON_API_KEY=your_key            # Для Ozon
ADMIN_ID=your_telegram_id        # Для админ-команд
WEBAPP_URL=https://your-url      # URL для Web App
```

---

## Решение проблем

### Бот не запускается

```bash
# Проверьте .env
cat .env

# Проверьте зависимости
pip install -r requirements.txt

# Проверьте токен
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

### Web App не открывается

- В локальной версии нужен публичный URL
- Сделайте деплой на Railway/Render
- Обновите WEBAPP_URL

### Конфликты с другими инстансами

Бот автоматически завершает конфликтующие процессы при запуске.

---

## Структура проекта

```
.
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── start.sh                     # Launch script
├── SETUP_GUIDE.md              # User-friendly setup guide
│
├── src/
│   ├── bot/
│   │   └── handlers.py         # Bot commands + Web App
│   └── core/
│       ├── config.py           # Configuration management
│       └── meta_guardian.py    # Monitoring (simplified)
│
└── webapp/
    ├── index.html              # Mini App interface
    └── server.py               # Web server
```

---

## Документация

- `SETUP_GUIDE.md` - Подробная инструкция для начинающих
- `.env.example` - Описание всех переменных окружения
- `README_BOLT.md` (этот файл) - Техническая документация

---

## API Endpoints (Web App Server)

```
GET  /              # Main Web App page
GET  /webapp        # Alternative route
GET  /api/status    # Bot status JSON
GET  /api/stats     # Statistics JSON
GET  /health        # Health check
```

---

## Что дальше

После успешного запуска:

1. Протестируйте бота (`/start`, `/panel`, `/status`)
2. Настройте Web App URL после деплоя
3. Добавьте дополнительные команды по необходимости
4. Интегрируйте с вашими AI сервисами
5. Расширьте функционал Web App

---

DOBRO. Precision. Reliability. Excellence.

Проект готов к работе и деплою.
