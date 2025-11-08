.PHONY: help guide cover test ozon-check env-template backup clean init-structure smoke lint fmt typecheck audit health verify guardian-start guardian-test

PYTHON := python
TOPIC ?= "Пассивный доход 2025"
TITLE ?= "Путеводитель"
STYLE ?= gradient
PRODUCT_ID ?= GF-2025-001

help:
	@echo "════════════════════════════════════════════════"
	@echo "  META-REPLIT · GuideFarm Mastery Coach"
	@echo "════════════════════════════════════════════════"
	@echo ""
	@echo "📚 КОНТЕНТ:"
	@echo "  make guide TOPIC='...'  - Создать гайд"
	@echo "  make cover TITLE='...'  - Создать обложку"
	@echo ""
	@echo "🚀 OZON:"
	@echo "  make ozon-check         - Проверить payload"
	@echo ""
	@echo "🧪 КАЧЕСТВО:"
	@echo "  make test               - Запустить тесты"
	@echo "  make smoke              - Smoke test"
	@echo "  make lint               - Linting"
	@echo "  make fmt                - Formatting"
	@echo "  make typecheck          - Type checking"
	@echo "  make audit              - Dependency audit"
	@echo "  make verify             - Run all quality checks"
	@echo ""
	@echo "🛠️  ИНФРА:"
	@echo "  make env-template       - Создать .env шаблон"
	@echo "  make backup             - Бэкап базы"
	@echo "  make init-structure     - Создать структуру"
	@echo "  make clean              - Очистка"
	@echo "  make health             - Health check"
	@echo ""
	@echo "🛡️  META-GUARDIAN:"
	@echo "  make guardian-start     - Запустить Guardian"
	@echo "  make guardian-test      - Тестировать Guardian"

guide:
	@echo "📝 Создание гайда: $(TOPIC)"
	@echo "⚠️  Используйте Telegram бот: /create"

cover:
	@echo "🎨 Создание обложки: $(TITLE)"
	@echo "⚠️  Используйте Telegram бот: /create"

# Тестирование
test:
	@echo "🧪 Запуск тестов..."
	@python -m pytest tests/ -v || echo "⚠️ Тесты не прошли"

smoke:
	@echo "💨 Smoke test: end-to-end генерация демо-гайда..."
	@SMOKE_TEST=1 python -c "from src.core.product import GuideFarm; gf = GuideFarm(); result = gf.run_full_pipeline('Python для начинающих', 'gemini', timeout=60); print('✅ Smoke test passed' if result else '❌ Failed')"

# Качество кода
lint:
	@echo "🔍 Проверка кода (ruff)..."
	@ruff check src/ tests/ || echo "⚠️ Найдены проблемы"

fmt:
	@echo "🎨 Форматирование кода (black)..."
	@black src/ tests/ || echo "⚠️ Форматирование не применено"

typecheck:
	@echo "🔎 Проверка типов (mypy)..."
	@mypy src/ --ignore-missing-imports || echo "⚠️ Проблемы с типами"

# Безопасность
audit:
	@echo "🔒 Аудит зависимостей..."
	@pip-audit || echo "⚠️ Найдены уязвимости"

# Мониторинг
health:
	@echo "❤️ Health check..."
	@python healthcheck.py

# Утилиты
backup:
	@echo "💾 Создание бэкапа базы данных..."
	@python scripts/backup_db.py

ozon-check:
	@echo "🛒 Проверка Ozon API конфигурации..."
	@python -c "from src.ozon.uploader import AIUploader; u = AIUploader(); print('✅ Ozon API настроен' if u.client_id and u.api_key else '❌ Отсутствуют OZON_CLIENT_ID или OZON_API_KEY')"

clean:
	@echo "🧹 Очистка..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Готово!"

init-structure:
	@echo "📁 Создание структуры..."
	@mkdir -p src/bot src/ai src/design src/ozon src/core
	@mkdir -p tests process compliance analytics scripts backups
	@mkdir -p guides covers ozon_payloads
	@touch src/__init__.py src/bot/__init__.py src/ai/__init__.py
	@touch src/design/__init__.py src/ozon/__init__.py src/core/__init__.py
	@echo "✅ Структура создана!"

env-template:
	@echo "🔐 Создание .env.template..."
	@echo "# GuideFarm Bot - Environment Variables" > .env.template
	@echo "TELEGRAM_BOT_TOKEN=your_bot_token" >> .env.template
	@echo "OPENAI_API_KEY=sk-..." >> .env.template
	@echo "GEMINI_API_KEY=..." >> .env.template
	@echo "XAI_API_KEY=xai-..." >> .env.template
	@echo "OZON_CLIENT_ID=..." >> .env.template
	@echo "OZON_API_KEY=..." >> .env.template
	@echo "✅ Создан: .env.template"

# Комплексная проверка
verify: health lint smoke ozon-check
	@echo "✅ Полная проверка качества завершена"

.PHONY: guardian-start
guardian-start:
	@echo "🛡️ Запуск META-GUARDIAN..."
	@python -c "from src.core.meta_guardian import start_guardian; g = start_guardian(); import time; time.sleep(3600)"

.PHONY: guardian-test
guardian-test:
	@echo "🧪 Тестирование META-GUARDIAN..."
	@python -c "from src.core.meta_guardian import MetaGuardian; g = MetaGuardian(check_interval=5); g.start(); import time; time.sleep(30); g.stop(); print(g.get_status_report())"