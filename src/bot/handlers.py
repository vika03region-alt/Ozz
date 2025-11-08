#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot Handlers for GuideFarm
Includes Web App support for mini-application
"""
import os
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logger = logging.getLogger(__name__)


class GuideFarmBot:
    """Main bot class with Web App support"""

    def __init__(self, token: str, guardian=None):
        """Initialize bot with token"""
        self.token = token
        self.guardian = guardian
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
        logger.info("GuideFarmBot initialized")

    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Basic commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("panel", self.panel_command))
        self.app.add_handler(CommandHandler("app", self.panel_command))
        self.app.add_handler(CommandHandler("status", self.status_command))

        # Callback handlers for Web App data
        self.app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.handle_web_app_data))

        logger.info("Handlers registered")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
Привет, {user.first_name}!

Я GuideFarm Bot - создаю цифровые гайды с помощью AI.

Основные команды:
/panel - Открыть панель управления
/status - Проверить статус системы
/help - Показать справку

DOBRO. Система запущена.
"""
        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
КОМАНДЫ БОТА:

/start - Начать работу
/panel - Открыть панель управления (Web App)
/app - Альтернативная команда для панели
/status - Статус системы
/help - Эта справка

ПАНЕЛЬ УПРАВЛЕНИЯ:
Используйте /panel для доступа к веб-интерфейсу управления ботом.

DOBRO. Поддержка активна.
"""
        await update.message.reply_text(help_text)

    async def panel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /panel command - opens Web App"""
        # В production здесь должен быть реальный URL вашего деплоя
        # Например: https://your-app.railway.app или https://your-app.render.com
        webapp_url = os.getenv('WEBAPP_URL', 'https://your-domain.com/webapp')

        # Создаем кнопку с Web App
        keyboard = [
            [InlineKeyboardButton("Открыть панель управления", web_app=WebAppInfo(url=webapp_url))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
ПАНЕЛЬ УПРАВЛЕНИЯ

Нажмите кнопку ниже для открытия веб-интерфейса.

В панели доступно:
- Статус бота (онлайн/офлайн)
- Отправка команд боту
- Просмотр логов
- Управление настройками

DOBRO. Панель готова.
"""
        await update.message.reply_text(text, reply_markup=reply_markup)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        from src.core.config import validate_config

        try:
            config = validate_config()

            status_text = """
СТАТУС СИСТЕМЫ

Telegram Bot: ONLINE
AI Providers:
"""
            if config.openai_api_key:
                status_text += "  - OpenAI GPT: OK\n"
            if config.gemini_api_key:
                status_text += "  - Google Gemini: OK\n"
            if config.xai_api_key:
                status_text += "  - xAI Grok: OK\n"

            if config.ozon_client_id and config.ozon_api_key:
                status_text += "\nOzon Integration: OK"
            else:
                status_text += "\nOzon Integration: Not configured"

            if config.supabase_url and config.supabase_key:
                status_text += "\nSupabase Database: OK"
            else:
                status_text += "\nSupabase Database: Not configured"

            status_text += "\n\nDOBRO. Все системы работают."

            await update.message.reply_text(status_text)

        except Exception as e:
            await update.message.reply_text(f"Ошибка проверки статуса: {str(e)}")

    async def handle_web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle data sent from Web App"""
        data = update.effective_message.web_app_data.data
        logger.info(f"Received Web App data: {data}")

        # Обработка данных из Web App
        await update.message.reply_text(
            f"Получены данные из панели:\n{data}\n\nDOBRO. Обработано."
        )

    def run(self, use_webhook: bool = False, webhook_url: str = None, port: int = 5000):
        """Run the bot"""
        if use_webhook and webhook_url:
            logger.info(f"Starting bot with webhook: {webhook_url}")
            self.app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
        else:
            logger.info("Starting bot with polling")
            self.app.run_polling(drop_pending_updates=True)
