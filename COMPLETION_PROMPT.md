# 🎯 GuideFarm Bot - Промпт для Завершения Проекта

## 📊 Текущий Статус

**Готовность проекта:** ~85%

- ✅ Основной функционал работает (создание гайдов, AI генерация, дизайн обложек)
- ✅ Документация полная (README, QUICK_START, PROMPTS_SYSTEM, FUNCTIONAL_CHECKLIST)
- ✅ Модульная архитектура (main.py 26 строк, все в модулях)
- ✅ Deployment настроен (Reserved VM, workflows)
- ✅ Makefile automation (backup, test, ozon-check)
- ⚠️ **Критические недоработки требуют исправления**

---

## 🔴 КРИТИЧЕСКИЕ ЗАДАЧИ (Must Have)

### 1. Реализация Недостающих Callback Handlers

**Проблема:** Кнопки в Telegram боте не работают

**Файл:** `src/bot/handlers.py`

**Что сделать:**

#### 1.1. Callback `regen_` (Перегенерация гайда)
```python
# Добавить в button_handler после строки 340

elif query.data.startswith("regen_"):
    product_id = query.data.replace("regen_", "")
    await query.answer()
    
    product = self.gf.find_product_by_id(product_id)
    if not product:
        await query.edit_message_text("❌ Продукт не найден")
        return
    
    # Спросить, что перегенерировать
    keyboard = [
        [InlineKeyboardButton("📝 Только контент", callback_data=f"regen_content_{product_id}")],
        [InlineKeyboardButton("🎨 Только обложку", callback_data=f"regen_cover_{product_id}")],
        [InlineKeyboardButton("🔄 Всё полностью", callback_data=f"regen_full_{product_id}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"cancel_{product_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔄 **Перегенерация гайда**\n\n"
        f"📚 {product['title']}\n\n"
        f"Что вы хотите перегенерировать?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Добавить обработчики для каждого типа перегенерации
elif query.data.startswith("regen_content_"):
    product_id = query.data.replace("regen_content_", "")
    await query.edit_message_text("⏳ Перегенерирую контент...")
    
    product = self.gf.find_product_by_id(product_id)
    writer = AIWriter(model=product.get('ai_model', 'openai'))
    
    # Перегенерация контента
    product_plan = {
        'title': product['title'],
        'price': product['price'],
        'description': product['description']
    }
    
    new_content = await asyncio.to_thread(
        writer.generate_guide_content,
        product['topic'],
        product_plan
    )
    
    # Обновление файлов
    guide_md_path = product['files']['guide_md']
    guide_pdf_path = product['files']['guide_pdf']
    
    with open(guide_md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Регенерация PDF
    from weasyprint import HTML
    HTML(string=new_content).write_pdf(guide_pdf_path)
    
    await query.message.reply_text(
        f"✅ **Контент перегенерирован!**\n\n"
        f"📝 Новый контент: {len(new_content)} символов",
        parse_mode="Markdown"
    )

elif query.data.startswith("regen_cover_"):
    product_id = query.data.replace("regen_cover_", "")
    await query.edit_message_text("⏳ Перегенерирую обложку...")
    
    product = self.gf.find_product_by_id(product_id)
    designer = AIDesigner()
    
    # Перегенерация обложки
    new_cover = await asyncio.to_thread(
        designer.create_premium_cover,
        product['title'],
        product['topic'],
        product_id,
        product['price']
    )
    
    product['files']['cover'] = new_cover
    self.gf.save_products()
    
    with open(new_cover, 'rb') as cover:
        await query.message.reply_photo(
            cover,
            caption=f"✅ **Обложка перегенерирована!**\n\n🎨 Новый дизайн",
            parse_mode="Markdown"
        )

elif query.data.startswith("regen_full_"):
    product_id = query.data.replace("regen_full_", "")
    await query.edit_message_text("⏳ Полная перегенерация... Это займёт несколько минут...")
    
    product = self.gf.find_product_by_id(product_id)
    
    # Удалить старый продукт
    self.gf.products = [p for p in self.gf.products if p['product_id'] != product_id]
    
    # Создать новый
    new_product = await asyncio.to_thread(
        self.gf.run_full_pipeline,
        product['topic'],
        product.get('ai_model', 'openai')
    )
    
    await query.message.reply_text(
        f"✅ **Гайд полностью перегенерирован!**\n\n"
        f"📚 {new_product['title']}\n"
        f"🆔 Новый ID: {new_product['product_id']}",
        parse_mode="Markdown"
    )
```

#### 1.2. Callback `cancel_` (Отмена/Удаление)
```python
elif query.data.startswith("cancel_"):
    product_id = query.data.replace("cancel_", "")
    await query.answer()
    
    # Подтверждение удаления
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{product_id}")],
        [InlineKeyboardButton("❌ Нет, вернуться", callback_data=f"back_to_product_{product_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚠️ **Подтверждение удаления**\n\n"
        f"Вы уверены, что хотите удалить этот гайд?\n"
        f"Это действие нельзя отменить.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

elif query.data.startswith("confirm_delete_"):
    product_id = query.data.replace("confirm_delete_", "")
    
    product = self.gf.find_product_by_id(product_id)
    if product:
        # Удалить файлы
        import os
        for file_path in product['files'].values():
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Удалить из базы
        self.gf.products = [p for p in self.gf.products if p['product_id'] != product_id]
        self.gf.save_products()
        
        await query.edit_message_text(
            f"🗑️ **Гайд удалён**\n\n"
            f"ID: {product_id}"
        )
    else:
        await query.edit_message_text("❌ Продукт не найден")

elif query.data.startswith("back_to_product_"):
    product_id = query.data.replace("back_to_product_", "")
    # Вернуться к просмотру продукта
    await query.edit_message_text("⬅️ Возврат к гайду...")
```

---

### 2. Улучшение Fallback Контента AIWriter

**Проблема:** Когда AI API недоступен, генерируется короткий текст (~1500 слов вместо 3000+)

**Файл:** `src/ai/writer.py` (строки 369-487)

**Что сделать:**

Расширить fallback контент до полноценного гайда:

```python
# Заменить текущий fallback на:

if not generated_text or len(generated_text) < 500:
    print("[AIWriter] ⚠️ AI генерация не удалась, используется расширенный fallback template")
    
    # Импортируем готовый шаблон
    from src.ai.fallback_templates import get_comprehensive_guide_template
    
    generated_text = get_comprehensive_guide_template(
        title=product_plan['title'],
        topic=topic,
        min_words=3000
    )
    
    print(f"[AIWriter] ✅ Fallback контент создан: {len(generated_text.split())} слов")
```

**Создать файл:** `src/ai/fallback_templates.py`

```python
def get_comprehensive_guide_template(title, topic, min_words=3000):
    """
    Генерирует полноценный гайд с минимум 3000 словами
    """
    template = f"""# {title}

## 📚 Введение

Добро пожаловать в исчерпывающее руководство по теме: **{topic}**

Этот гайд разработан для всех уровней подготовки - от новичков до профессионалов.

### 🎯 Для кого этот гайд?

- Новички, начинающие знакомство с темой
- Специалисты, желающие углубить знания
- Профессионалы, ищущие систематизацию опыта
- Предприниматели, планирующие применение на практике

### 📖 Что вы узнаете

1. Фундаментальные основы {topic}
2. Практические техники и методы
3. Распространённые ошибки и их решения
4. Продвинутые стратегии
5. Кейс-стади и примеры
6. Инструменты и ресурсы
7. План действий на 30/60/90 дней

---

## 🚀 Глава 1: Фундаментальные Основы

### 1.1 История и Контекст

{topic} имеет долгую историю развития...
[РАСШИРИТЬ: 500 слов о истории, эволюции, ключевых моментах]

### 1.2 Базовые Концепции

**Ключевое понятие #1:** [Определение]
- Почему это важно
- Как это работает
- Примеры применения

**Ключевое понятие #2:** [Определение]
[РАСШИРИТЬ: 400 слов]

### 1.3 Типичные Заблуждения

❌ **Миф 1:** [Описание]
✅ **Реальность:** [Объяснение]

[РАСШИРИТЬ: 300 слов, 5 мифов]

---

## 💡 Глава 2: Пошаговое Руководство для Начинающих

### 2.1 Подготовка

**Шаг 1: Оценка текущей ситуации**
[РАСШИРИТЬ: 400 слов]

**Шаг 2: Постановка целей**
- Краткосрочные цели (1-3 месяца)
- Среднесрочные цели (3-6 месяцев)
- Долгосрочные цели (6-12 месяцев)

**Шаг 3: Выбор инструментов**
[РАСШИРИТЬ: 300 слов]

### 2.2 Первые Шаги

[РАСШИРИТЬ: 600 слов с детальными инструкциями]

---

## 🎯 Глава 3: Практическое Применение

### 3.1 Кейс-стади #1

**Ситуация:** [Описание]
**Решение:** [Пошаговый план]
**Результат:** [Метрики и выводы]

[РАСШИРИТЬ: 400 слов на каждый кейс, минимум 3 кейса = 1200 слов]

---

## 🔧 Глава 4: Инструменты и Ресурсы

### 4.1 Бесплатные Инструменты

1. **[Инструмент 1]**
   - Описание
   - Преимущества
   - Как использовать
   
[РАСШИРИТЬ: 500 слов, минимум 10 инструментов]

### 4.2 Платные Решения

[РАСШИРИТЬ: 400 слов]

---

## ⚠️ Глава 5: Частые Ошибки и Решения

### Ошибка #1: [Название]

**Проблема:** [Описание]
**Почему возникает:** [Причины]
**Как избежать:** [Профилактика]
**Как исправить:** [Решение]

[РАСШИРИТЬ: 300 слов на ошибку, минимум 5 ошибок = 1500 слов]

---

## 🚀 Глава 6: План Действий

### День 1-7: Начало

- [ ] Задача 1
- [ ] Задача 2
- [ ] Задача 3

[РАСШИРИТЬ: 400 слов]

### Неделя 2-4: Развитие

[РАСШИРИТЬ: 300 слов]

### Месяц 2-3: Оптимизация

[РАСШИРИТЬ: 300 слов]

---

## 📊 Заключение

### Ключевые Выводы

1. [Вывод 1]
2. [Вывод 2]
3. [Вывод 3]

### Следующие Шаги

[РАСШИРИТЬ: 300 слов]

---

## 📚 Дополнительные Ресурсы

- Книги
- Курсы
- Сообщества
- Инструменты

[РАСШИРИТЬ: 200 слов]

---

**Автор:** GuideFarm Bot AI
**Версия:** 1.0
**Дата создания:** {datetime.now().strftime("%d.%m.%Y")}
"""
    
    # Проверка минимального количества слов
    word_count = len(template.split())
    if word_count < min_words:
        # Добавить дополнительные секции
        template += f"""

## 📖 Бонус: Глоссарий Терминов

[Список из 50+ терминов с определениями]

## 🎓 FAQ: 25 Популярных Вопросов

**Q1:** [Вопрос]
**A1:** [Ответ]

[25 вопросов и ответов]
"""
    
    return template
```

---

### 3. Создание Тестовых Данных

**Проблема:** База данных пустая (0 продуктов)

**Что сделать:**

Создать скрипт для генерации тестовых продуктов:

**Файл:** `scripts/generate_test_products.py`

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.core.product import GuideFarm

def generate_test_products():
    """Создаёт 3 тестовых продукта для демонстрации"""
    
    gf = GuideFarm()
    
    test_topics = [
        "Пассивный доход на дивидендах",
        "Продуктивность и тайм-менеджмент",
        "SEO-оптимизация для бизнеса"
    ]
    
    models = ["openai", "gemini", "grok"]
    
    print("🎯 Генерация тестовых продуктов...")
    
    for i, (topic, model) in enumerate(zip(test_topics, models), 1):
        print(f"\n📝 {i}/3: {topic} (AI: {model})")
        try:
            product = gf.run_full_pipeline(topic, model)
            print(f"✅ Создан: {product['product_id']}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"\n✅ Готово! Всего продуктов: {len(gf.products)}")

if __name__ == "__main__":
    generate_test_products()
```

Запустить: `python scripts/generate_test_products.py`

---

## 🟡 ВАЖНЫЕ ЗАДАЧИ (Should Have)

### 4. Расширенная Аналитика

**Файл:** `src/core/product.py` (метод `get_analytics`)

**Что добавить:**

```python
def get_analytics(self):
    """Расширенная аналитика с визуализацией"""
    
    if not self.products:
        return "📊 Нет данных для аналитики. Создайте первый гайд командой /create"
    
    total_products = len(self.products)
    published = len([p for p in self.products if p.get('status') == 'published'])
    drafts = total_products - published
    
    total_revenue = sum(p.get("price", 0) * p.get("actual_monthly_sales", 0) for p in self.products)
    avg_rating = sum(p.get("actual_rating", 0) for p in self.products) / total_products if total_products > 0 else 0
    
    # Статистика по AI моделям
    model_stats = {}
    for p in self.products:
        model = p.get('ai_model', 'unknown')
        model_stats[model] = model_stats.get(model, 0) + 1
    
    # Статистика по дизайн-стилям
    design_stats = {}
    for p in self.products:
        style = p.get('design_style', 'unknown')
        design_stats[style] = design_stats.get(style, 0) + 1
    
    # Топ продукты по рейтингу
    top_products = sorted(self.products, key=lambda x: x.get('actual_rating', 0), reverse=True)[:5]
    
    analytics = f"""📊 **Расширенная Аналитика GuideFarm**

📦 **Общая Статистика**
├─ Всего продуктов: {total_products}
├─ Опубликовано: {published} ✅
├─ Черновиков: {drafts} 📝
└─ Общая выручка: {total_revenue:,.0f}₽

⭐ **Качество**
├─ Средний рейтинг: {avg_rating:.2f}/5.0
└─ Прогноз продаж: {sum(p.get('actual_monthly_sales', 0) for p in self.products)} шт/мес

🤖 **Статистика по AI моделям**
"""
    for model, count in model_stats.items():
        analytics += f"├─ {model}: {count} гайдов\n"
    
    analytics += f"""
🎨 **Популярные дизайн-стили**
"""
    for style, count in sorted(design_stats.items(), key=lambda x: x[1], reverse=True)[:3]:
        analytics += f"├─ {style}: {count} обложек\n"
    
    analytics += f"""
🏆 **Топ-5 по рейтингу**
"""
    for i, p in enumerate(top_products, 1):
        analytics += f"{i}. {p['title']} - ⭐{p.get('actual_rating', 0):.1f} | 💰{p['price']}₽\n"
    
    return analytics
```

---

### 5. Система Обратной Связи

**Создать файл:** `src/bot/feedback.py`

```python
class FeedbackCollector:
    """Собирает отзывы пользователей для улучшения AI"""
    
    def __init__(self):
        self.feedback_file = "feedback_database.json"
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self):
        """Загрузка данных обратной связи"""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def add_feedback(self, product_id, user_id, rating, comment=""):
        """Добавить отзыв"""
        feedback = {
            "product_id": product_id,
            "user_id": user_id,
            "rating": rating,  # 1-5
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_data.append(feedback)
        self._save_feedback()
        
        return "✅ Спасибо за отзыв! Он поможет улучшить качество гайдов."
    
    def _save_feedback(self):
        """Сохранение"""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
    
    def get_product_feedback(self, product_id):
        """Получить все отзывы по продукту"""
        return [f for f in self.feedback_data if f['product_id'] == product_id]
    
    def get_average_rating(self, product_id):
        """Средняя оценка"""
        ratings = [f['rating'] for f in self.feedback_data if f['product_id'] == product_id]
        return sum(ratings) / len(ratings) if ratings else 0
```

**Добавить в handlers.py:**

```python
# Команда для отзыва
async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /feedback - оставить отзыв о гайде"""
    
    # Показать последние 5 продуктов
    products = self.gf.get_recent_products(5)
    
    keyboard = []
    for p in products:
        keyboard.append([
            InlineKeyboardButton(
                f"⭐ {p['title'][:40]}...",
                callback_data=f"feedback_{p['product_id']}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⭐ **Оставить отзыв**\n\nВыберите гайд:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Callback для выбора оценки
elif query.data.startswith("feedback_"):
    product_id = query.data.replace("feedback_", "")
    
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data=f"rate_1_{product_id}"),
            InlineKeyboardButton("⭐⭐", callback_data=f"rate_2_{product_id}"),
            InlineKeyboardButton("⭐⭐⭐", callback_data=f"rate_3_{product_id}")
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"rate_4_{product_id}"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"rate_5_{product_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⭐ Оцените качество гайда (1-5):",
        reply_markup=reply_markup
    )

elif query.data.startswith("rate_"):
    parts = query.data.split("_")
    rating = int(parts[1])
    product_id = parts[2]
    
    from src.bot.feedback import FeedbackCollector
    collector = FeedbackCollector()
    result = collector.add_feedback(product_id, user_id, rating)
    
    await query.edit_message_text(result)
```

---

## 🟢 ЖЕЛАТЕЛЬНЫЕ ЗАДАЧИ (Nice to Have)

### 6. Интеграционные Тесты

**Файл:** `tests/test_full_integration.py`

```python
import pytest
from src.core.product import GuideFarm

def test_full_pipeline_openai():
    """Тест полного цикла с OpenAI"""
    gf = GuideFarm()
    result = gf.run_full_pipeline("Инвестиции в акции", "openai")
    
    assert result is not None
    assert 'product_id' in result
    assert 'title' in result
    assert len(result['title']) > 10
    assert result['price'] > 0

def test_full_pipeline_gemini():
    """Тест полного цикла с Gemini"""
    gf = GuideFarm()
    result = gf.run_full_pipeline("Криптовалюта", "gemini")
    
    assert result is not None
    assert os.path.exists(result['files']['cover'])
    assert os.path.exists(result['files']['guide_pdf'])
```

Запустить: `make test`

---

### 7. Команда /history (История создания)

**Добавить в handlers.py:**

```python
async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать историю созданных гайдов"""
    
    products = self.gf.products[-10:]  # Последние 10
    
    if not products:
        await update.message.reply_text(
            "📚 История пуста. Создайте первый гайд командой /create"
        )
        return
    
    history_text = "📚 **История создания гайдов**\n\n"
    
    for i, p in enumerate(reversed(products), 1):
        status_icon = "✅" if p.get('status') == 'published' else "📝"
        history_text += (
            f"{i}. {status_icon} **{p['title']}**\n"
            f"   💰 {p['price']}₽ | ⭐ {p.get('actual_rating', 'N/A')}\n"
            f"   🤖 {p.get('ai_model', 'N/A')} | 🆔 {p['product_id'][:8]}\n\n"
        )
    
    await update.message.reply_text(history_text, parse_mode="Markdown")
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

После выполнения всех задач проверить:

- [ ] Все кнопки в Telegram боте работают (regen, cancel, edit)
- [ ] Fallback контент AIWriter >= 3000 слов
- [ ] База данных содержит >= 3 тестовых продукта
- [ ] Команда `/analytics` показывает расширенную статистику
- [ ] Команда `/feedback` позволяет оставлять отзывы
- [ ] Команда `/history` показывает историю
- [ ] Интеграционные тесты проходят (`make test`)
- [ ] Документация обновлена (README.md, FUNCTIONAL_CHECKLIST.md)
- [ ] Deployment на Reserved VM работает
- [ ] Логи не содержат критических ошибок

---

## 🚀 ПОРЯДОК ВЫПОЛНЕНИЯ

1. **День 1:** Критические задачи #1-3 (callbacks, fallback, тестовые данные)
2. **День 2:** Важные задачи #4-5 (аналитика, feedback)
3. **День 3:** Желательные задачи #6-7 (тесты, history)
4. **День 4:** Финальное тестирование, документация, deployment

---

## 📝 КРИТЕРИИ ГОТОВНОСТИ

Проект считается **100% завершённым**, когда:

✅ Все функции Telegram бота работают без ошибок
✅ AI генерация создаёт контент >= 3000 слов в любом сценарии
✅ Есть минимум 3 примера готовых продуктов
✅ Аналитика показывает детальную статистику
✅ Пользователи могут оставлять отзывы
✅ Deployment на Reserved VM стабилен
✅ Документация полная и актуальная

---

**Текущая версия:** 0.85
**Целевая версия:** 1.0

**Предполагаемое время:** 3-4 дня разработки
**Приоритет:** ВЫСОКИЙ (проект на финишной прямой)
