
# -*- coding: utf-8 -*-
"""
GuideFarm Bot - Автоматизированное создание цифровых гайдов
META-REPLIT Mastery Coach Edition
"""
import os
import sys
import io
import signal
import time
import logging

# UTF-8 кодировка для всего приложения
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорты из модулей
from src.core.config import validate_config, ConfigurationError
from src.bot.handlers import GuideFarmBot

def kill_conflicting_instances():
    """Убить все конфликтующие экземпляры бота"""
    import subprocess
    
    try:
        # Найти все процессы python main.py кроме текущего
        result = subprocess.run(
            ["pgrep", "-f", "python.*main.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            current_pid = str(os.getpid())
            
            for pid in pids:
                if pid and pid != current_pid:
                    logger.warning(f"Обнаружен конфликтующий процесс PID {pid}, завершаю...")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        # Если не завершился - убить жестко
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Процесс уже завершен
                        logger.info(f"Процесс PID {pid} завершен")
                    except Exception as e:
                        logger.warning(f"Не удалось завершить процесс {pid}: {e}")
            
            # Дать время на полное освобождение Telegram API
            if len(pids) > 1:
                logger.info("Ожидание освобождения Telegram API (5 секунд)...")
                time.sleep(5)
                
    except Exception as e:
        logger.warning(f"Ошибка при поиске конфликтующих процессов: {e}")

def is_deployment():
    """Проверить, запущен ли в deployment режиме"""
    return (
        os.getenv('REPL_DEPLOYMENT') == '1' or 
        os.getenv('REPL_DEPLOYMENT_TYPE') == 'production'
    )

def check_if_should_run():
    """Определить, нужно ли запускать бота"""
    in_deployment = is_deployment()
    
    if not in_deployment:
        logger.info("="*70)
        logger.info("🤖 WORKSPACE РЕЖИМ")
        logger.info("="*70)
        logger.info("Бот запускается автоматически")
        logger.info("Для production используйте: Deploy → Reserved VM")
        logger.info("="*70)
    else:
        logger.info("="*70)
        logger.info("🚀 PRODUCTION РЕЖИМ (Reserved VM)")
        logger.info("="*70)
    
    return True

if __name__ == "__main__":
    # Проверить, нужно ли запускать бота
    if not check_if_should_run():
        sys.exit(0)
    
    logger.info("🚀 Запуск GuideFarm Bot...")
    logger.info("━" * 50)
    logger.info("META-REPLIT Mastery Coach System активирован!")
    logger.info("Модульная архитектура: ✅")
    logger.info("━" * 50)
    
    # Автоматически убить конфликтующие экземпляры
    logger.info("🔍 Проверка на конфликтующие экземпляры...")
    kill_conflicting_instances()
    
    # Инициализация переменных перед try блоком
    guardian = None
    
    try:
        # Валидация конфигурации и secrets
        logger.info("🔧 Проверка конфигурации...")
        config = validate_config()
        config.print_status()
        logger.info("✅ Конфигурация проверена, запуск бота...")
        
        # 🛡️ ЗАПУСК META-GUARDIAN (опционально)
        try:
            logger.info("🛡️ Запуск META-GUARDIAN (автономная система защиты)...")
            from src.core.meta_guardian import start_guardian
            guardian = start_guardian(check_interval=60)
            logger.info("✅ META-GUARDIAN активирован")
        except Exception as e:
            logger.warning(f"META-GUARDIAN недоступен: {e}")
            logger.info("Бот запустится без дополнительного мониторинга")
        
        # Запуск бота с токеном из конфигурации
        token = config.get_required("TELEGRAM_BOT_TOKEN")
        bot = GuideFarmBot(token=token, guardian=guardian)
        logger.info("✅ Бот инициализирован")
        
        # Автоопределение режима работы
        in_deployment = is_deployment()
        
        if in_deployment:
            # В deployment используем webhook для полного избежания конфликтов
            webhook_url = os.getenv('REPL_DEPLOYMENT_URL')
            if webhook_url:
                logger.info(f"🌐 DEPLOYMENT РЕЖИМ: Webhook на {webhook_url}")
                logger.info("✅ Конфликты с polling невозможны")
                bot.run(use_webhook=True, webhook_url=webhook_url, port=5000)
            else:
                # Fallback на polling если URL не найден
                logger.warning("REPL_DEPLOYMENT_URL не найден")
                logger.info("🤖 Использую polling режим с автоконтролем конфликтов")
                bot.run(use_webhook=False)
        else:
            # В development используем polling
            logger.info("🤖 DEVELOPMENT РЕЖИМ: Polling")
            logger.info("✅ Конфликтующие экземпляры автоматически завершены")
            bot.run(use_webhook=False)
            
    except ConfigurationError as e:
        logger.error(f"{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("⏹️ Остановка бота...")
        if guardian is not None:
            try:
                guardian.stop()
                logger.info("✅ META-GUARDIAN остановлен")
            except:
                pass
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
