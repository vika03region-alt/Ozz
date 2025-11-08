#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Healthcheck script для мониторинга GuideFarm Bot
Использование: python healthcheck.py
"""
import sys
import json
from pathlib import Path
import os

def check_secrets():
    """Проверка наличия обязательных секретов"""
    issues = []
    required_secrets = ["TELEGRAM_BOT_TOKEN"]
    # Хотя бы один AI provider должен быть
    ai_providers = ["OPENAI_API_KEY", "GEMINI_API_KEY", "XAI_API_KEY"]
    
    for secret in required_secrets:
        if not os.getenv(secret):
            issues.append(f"❌ Не настроен секрет: {secret}")
    
    # Проверяем что хотя бы один AI provider есть
    if not any(os.getenv(provider) for provider in ai_providers):
        issues.append(f"❌ Отсутствуют все AI provider keys (нужен хотя бы один)")
    
    return {"status": "ok" if not issues else "error", "message": "\n".join(issues) if issues else "Все секреты настроены"}

def check_ai_providers():
    """Проверка доступности AI провайдеров (базовая)"""
    issues = []
    # Здесь можно добавить более детальные проверки, например, запросы к API
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("❌ Отсутствует OPENAI_API_KEY")
    return {"status": "ok" if not issues else "error", "message": "\n".join(issues) if issues else "AI провайдеры доступны"}

def check_database():
    """Проверка JSON базы данных"""
    db_path = "products_database.json"
    if not os.path.exists(db_path):
        return {"status": "warning", "message": "База данных не найдена (будет создана при первом запуске)"}

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {"status": "ok", "message": f"База содержит {len(data)} продуктов"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка чтения БД: {e}"}

def check_pipeline_smoke():
    """Smoke test: проверка что pipeline может запуститься"""
    if os.getenv('SMOKE_TEST') != '1':
        return {"status": "skipped", "message": "Smoke test отключен (включить: SMOKE_TEST=1)"}

    try:
        from src.core.product import GuideFarm
        gf = GuideFarm()
        # Проверяем что можем создать экземпляр и у него есть методы
        if hasattr(gf, 'run_full_pipeline'):
            return {"status": "ok", "message": "Pipeline готов к запуску"}
        else:
            return {"status": "error", "message": "Pipeline не содержит метод run_full_pipeline"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка инициализации pipeline: {e}"}


def check_directories():
    """Проверка наличия необходимых директорий"""
    issues = []
    required_dirs = ["src", "data", "logs", "output"]
    for dir_path in required_dirs:
        if not Path(dir_path).is_dir():
            issues.append(f"❌ Отсутствует директория: {dir_path}")
    return {"status": "ok" if not issues else "error", "message": "\n".join(issues) if issues else "Все директории на месте"}

def check_health():
    """Проверка здоровья системы"""
    print("🚀 Запуск health check...\n")

    # Запуск всех проверок
    checks = {
        "secrets": check_secrets(),
        "ai_providers": check_ai_providers(),
        "database": check_database(),
        "directories": check_directories(),
        "pipeline_smoke": check_pipeline_smoke()
    }

    # Сбор результатов
    all_ok = True
    results = []
    for name, result in checks.items():
        status = result.get("status", "unknown")
        message = result.get("message", "Нет сообщения")
        if status not in ["ok", "skipped"]:
            all_ok = False
        results.append(f"[{status.upper()}] {name}: {message.replace(chr(10), chr(10)+'    ')}") # Отступы для многострочных сообщений

    # Вывод результата
    print("\n" + "="*30)
    if all_ok:
        print("✅ GuideFarm Bot работает штатно!")
    else:
        print("🚨 ОБНАРУЖЕНЫ ПРОБЛЕМЫ:\n")
        for line in results:
            print(line)
    print("="*30 + "\n")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(check_health())