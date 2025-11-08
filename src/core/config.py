#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management for GuideFarm Bot
Handles environment variables and secrets validation
"""
import os
from typing import Optional
from dataclasses import dataclass


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


@dataclass
class Config:
    """Configuration container for GuideFarm Bot"""

    telegram_bot_token: str
    admin_id: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    ozon_client_id: Optional[str] = None
    ozon_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    def get_required(self, key: str) -> str:
        """Get required config value"""
        value = getattr(self, key.lower().replace('-', '_'), None)
        if not value:
            raise ConfigurationError(f"Missing required config: {key}")
        return value

    def has_ai_provider(self) -> bool:
        """Check if at least one AI provider is configured"""
        return any([self.openai_api_key, self.gemini_api_key, self.xai_api_key])

    def print_status(self):
        """Print configuration status"""
        print("\n" + "="*50)
        print("CONFIGURATION STATUS")
        print("="*50)
        print(f"Telegram Bot Token: {'OK' if self.telegram_bot_token else 'MISSING'}")
        print(f"Admin ID: {'OK' if self.admin_id else 'Not set'}")
        print(f"\nAI Providers:")
        print(f"  OpenAI: {'OK' if self.openai_api_key else 'MISSING'}")
        print(f"  Gemini: {'OK' if self.gemini_api_key else 'MISSING'}")
        print(f"  xAI Grok: {'OK' if self.xai_api_key else 'MISSING'}")
        print(f"\nOzon Integration:")
        print(f"  Client ID: {'OK' if self.ozon_client_id else 'Not set'}")
        print(f"  API Key: {'OK' if self.ozon_api_key else 'Not set'}")
        print(f"\nSupabase:")
        print(f"  URL: {'OK' if self.supabase_url else 'Not set'}")
        print(f"  Key: {'OK' if self.supabase_key else 'Not set'}")
        print("="*50 + "\n")


def validate_config() -> Config:
    """Validate and load configuration from environment variables"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        raise ConfigurationError(
            "TELEGRAM_BOT_TOKEN not found. Get one from @BotFather on Telegram."
        )

    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    xai_key = os.getenv('XAI_API_KEY')

    if not any([openai_key, gemini_key, xai_key]):
        raise ConfigurationError(
            "At least one AI provider key is required (OPENAI_API_KEY, GEMINI_API_KEY, or XAI_API_KEY)"
        )

    config = Config(
        telegram_bot_token=telegram_token,
        admin_id=os.getenv('ADMIN_ID'),
        openai_api_key=openai_key,
        gemini_api_key=gemini_key,
        xai_api_key=xai_key,
        ozon_client_id=os.getenv('OZON_CLIENT_ID'),
        ozon_api_key=os.getenv('OZON_API_KEY'),
        supabase_url=os.getenv('VITE_SUPABASE_URL'),
        supabase_key=os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
    )

    return config
