"""
FastAPI Telegram Webhook Integration
Adds /webhook/telegram endpoint to handle Telegram updates
"""

import logging
from fastapi import FastAPI, Request
from telegram import Update

logger = logging.getLogger(__name__)


def setup_telegram_webhook(app: FastAPI, bot_application) -> None:
    """
    Setup Telegram webhook endpoint in FastAPI
    
    Args:
        app: FastAPI application instance
        bot_application: The telegram.ext.Application instance from telegram_bot.py
    """
    
    @app.post("/webhook/telegram")
    async def telegram_webhook(request: Request):
        """
        Receive Telegram updates via webhook
        Called by Telegram servers when bot receives messages
        """
        try:
            data = await request.json()
            update = Update.de_json(data, bot_application.bot)
            await bot_application.process_update(update)
            logger.info(f"Processed Telegram update: {update.update_id}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Error processing Telegram webhook: {e}")
            return {"ok": False, "error": str(e)}

    @app.get("/webhook/telegram/health")
    async def telegram_webhook_health():
        """Health check for webhook"""
        return {"status": "ok", "webhook": "telegram"}

    logger.info("Telegram webhook endpoint registered at /webhook/telegram")