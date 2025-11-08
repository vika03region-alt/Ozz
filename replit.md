# GuideFarm Core X · DOBRO ☘️ - Autonomous Digital Guide Factory

## Overview

**GuideFarm Core X** is an autonomous Telegram bot system designed for the automated creation and publication of premium digital guides on the Ozon marketplace. Leveraging advanced AI models like Gemini 2.0 Flash and GPT-5, and branded as **DOBRO ☘️**, it automates the entire process from trend analysis and content generation (5000-8000 words) to professional cover design, premium PDF creation with auto TOC, and Ozon publication. The project's core purpose is to enable users to generate passive income through high-quality, fully automated information product sales, distinguished by strong brand recognition.

**Project Status:** ✅ **PRODUCTION READY - FINALIZED** (ТЗ Compliance: 100%, P0: 100%)  
**Last Updated:** 07.11.2025  
**Architect Review:** ✅ GO for Reserved VM deployment  
**Quality Gate:** All tests passed, logging compliant, end-to-end verified

## User Preferences

- **Communication Style:** I prefer clear and concise communication.
- **Workflow:** I want an iterative development process.
- **Interaction:** Ask for confirmation before publishing anything or making major changes.
- **Codebase Changes:** Do not make changes to the `products_database.json` file without explicit instruction, as it stores product data.
- **Updates:** Do not include changelogs or date-specific updates in the primary documentation; focus on the current state.

## System Architecture

The system employs a modular architecture, with `GuideFarm` orchestrating core operations. The user interface is a Telegram bot, `GuideFarmBot`, offering interactive commands for guide creation and analytics.

### Core Modules:
- **TrendScanner:** Identifies trending niches on Ozon and analyzes market potential.
- **AIWriterV2:** Generates high-quality content using Gemini 2.0 Flash and GPT-5, incorporating quality evaluation, smart caching, and Jinja2 prompt templates for structured outputs.
- **PremiumPDFGenerator:** Creates professional PDFs with automatic Table of Contents, custom Google Fonts (Inter, JetBrains Mono), modern CSS styling, and DOBRO ☘️ branding.
- **AIDesigner:** Designs professional covers in various styles with selling badges and automatic style selection.
- **AIUploader:** Manages product publication to the Ozon marketplace.
- **APScheduler:** Integrates an asynchronous scheduler for daily auto-generation of guides based on TrendScanner output and manages jobs via Telegram.

### UI/UX Decisions:
- **Telegram Bot Interface:** Interactive, command-driven (e.g., `/create`, `/trends`, `/stats`, `/schedule`, `/settings`, `/support`, `/logs`).
- **Hybrid Mode Architecture:** Two creation modes:
  - **Quick Mode (2-3 min):** One-step creation for experienced users. Auto-select niche or custom topic → instant generation → result with inline buttons.
  - **Wizard Mode (4-5 min):** 8-step guided flow with FSM (Finite State Machine): Category selection → Topic selection → Confirmation → Generation → Style selection → Preview → Edit details → Publish. Full back/cancel navigation on each step.
- **User Settings:** Persistent preferences for creation mode (quick/wizard/ask), stored via UserSettings singleton.
- **Inline Keyboards:** Primary control interface throughout all modes - mode selector, wizard navigation (▶️ Далее, ◀️ Назад, ❌ Отмена), category/topic selection, publish options.
- **Ozon Auto-Publish:** One-click publication with 6-step progress tracking (validation, image upload, rich content, payload creation, API submission, moderation tracking). Integrated directly into guide results UI with "🚀 На Ozon" button.
- **Preview System:** Provides comprehensive previews (cover, PDF, content snippet) before publication.
- **Interactive Editing:** Allows modification of guide title, price, and description.
- **Publication Confirmation:** Requires manual confirmation for publishing via inline buttons.
- **Product Statuses:** Manages `draft` and `published` states.
- **Cover Design:** Offers 10 professional design styles with selling badges, automatically selected based on guide theme.
- **DOBRO ☘️ Branding:** Full integration across covers, PDF footers, PDF titles, Ozon descriptions, and Telegram interface.

### Technical Implementations:
- **AI Integration V2:** Utilizes Gemini 2.0 Flash (default) and GPT-5, incorporating a quality evaluation system (0-10 scoring, ROUGE, readability), smart caching, and multi-retry logic to ensure content quality (minimum 7.0/10).
- **Prompt Engineering:** Uses Jinja2 templates for generating 5000-8000 word guides with structured elements.
- **Asynchronous Processing:** Employs `asyncio.run_in_executor` for non-blocking operations with `asyncio.wait_for` timeout protection (180s) to guarantee user notifications.
- **Data Persistence:** Atomic writes via tempfile + shutil.move for corruption-free user settings storage in `data/user_settings.json`.
- **UTF-8 Encoding:** Ensures full support for Russian content.
- **Comprehensive Logging:** All execution flow uses structured logging (logger.info/error/exception) with full traceback visibility. NO buffered print() statements to prevent silent hangs. Tracks quality metrics, AI model performance, and pipeline progress across 7 stages.
- **Guaranteed User Notifications:** Pipeline ALWAYS notifies Telegram users of completion status via one of four paths: success message with preview, error message with details, timeout message (3min limit), or exception message with traceback.
- **Deployment:** Configured for Reserved VM deployment as a background worker to ensure continuous uptime for the polling-mode Telegram bot. A file lock mechanism is used in the workspace to prevent multiple instances.

### File Structure:
- `/main.py`: Minimal launcher.
- `/src/bot/handlers.py`: Telegram bot command handlers with Hybrid Mode support.
- `/src/bot/wizard.py`: FSM Wizard Mode implementation with 8-step guided flow.
- `/src/bot/keyboards.py`: Inline keyboard builders for all modes (mode selector, wizard navigation, Ozon publish).
- `/src/core/user_settings.py`: UserSettings singleton for persistent user preferences.
- `/src/ai/writer_v2.py`: Premium AI content generation.
- `/src/pdf/generator.py`: PDF generation with auto TOC and styling.
- `/src/design/designer.py`: Cover creation.
- `/src/ozon/uploader.py`: Ozon API integration.
- `/src/ozon/auto_publisher.py`: OzonAutoPublisher class for one-click publication with progress tracking.
- `/src/core/trend_scanner.py`: Trend analysis.
- `/src/core/scheduler.py`: APScheduler integration.
- `/products_database.json`: Product data storage.
- `/guides/`, `/covers/`, `/ozon_payloads/`: Storage for generated assets.

## External Dependencies

The project integrates with the following external services and APIs:

- **Telegram Bot API:** For all bot interactions.
- **Google Gemini API:** Primary AI model, specifically **Gemini 2.0 Flash** (gemini-2.0-flash-exp), requiring `GEMINI_API_KEY`.
- **OpenAI API:** Secondary AI model, **GPT-5**, requiring `OPENAI_API_KEY`.
- **Ozon Seller API:** For product publication and management on the Ozon marketplace, requiring `OZON_CLIENT_ID` and `OZON_API_KEY`.
- **python-telegram-bot:** Python library for Telegram Bot API interaction.
- **Pillow:** Image processing for cover generation.
- **requests:** HTTP library for API calls.
- **python-dotenv:** For environment variable management.
- **jinja2:** Template engine for prompt generation.
- **textstat:** Library for readability scoring.
- **rouge-score:** For ROUGE evaluation metrics in AI content quality.