"""
Telegram Bot Integration for Onboarding Archaeologist
Handles /start, repo analysis, and Q&A via Telegram
"""

import os
import logging
from typing import Optional
import httpx

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Store user sessions for multi-step interactions
user_sessions: dict = {}


class TelegramBotManager:
    """Manages Telegram bot interactions with Onboarding Archaeologist backend"""

    def __init__(self):
        self.backend_url = BACKEND_URL
        self.http_client = httpx.AsyncClient(timeout=120.0)

    async def analyze_repo(self, owner: str, repo: str) -> dict:
        """Call backend /api/openclaw/analyze endpoint"""
        try:
            response = await self.http_client.post(
                f"{self.backend_url}/api/openclaw/analyze",
                json={"owner": owner, "repo": repo},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error analyzing {owner}/{repo}: {e}")
            raise

    async def ask_question(self, repository_id: int, question: str) -> dict:
        """Call backend /api/openclaw/ask endpoint"""
        try:
            response = await self.http_client.post(
                f"{self.backend_url}/api/openclaw/ask",
                json={"repository_id": repository_id, "question": question},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error answering question: {e}")
            raise

    async def get_latest_repo(self) -> Optional[dict]:
        """Get the latest analyzed repository"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/openclaw/repositories/latest"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error fetching latest repo: {e}")
            return None

    async def get_decisions(self, repository_id: int) -> dict:
        """Get architectural decisions for a repository"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/openclaw/repositories/{repository_id}/decisions"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error fetching decisions: {e}")
            raise

    async def get_bus_factor(self, repository_id: int) -> dict:
        """Get bus factor analysis for a repository"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/openclaw/repositories/{repository_id}/bus-factor"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error fetching bus factor: {e}")
            raise

    async def get_ghost_code(self, repository_id: int) -> dict:
        """Get ghost code analysis for a repository"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/openclaw/repositories/{repository_id}/ghost-code"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error fetching ghost code: {e}")
            raise

    async def get_onboarding_path(self, repository_id: int, level: str) -> dict:
        """Get onboarding path for a repository"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/openclaw/repositories/{repository_id}/onboarding/{level}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Backend error fetching onboarding path: {e}")
            raise


# Initialize bot manager
bot_manager = TelegramBotManager()


# ============================================================================
# Command Handlers
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    welcome_text = (
        "👋 *Welcome to Onboarding Archaeologist!*\n\n"
        "I help you analyze GitHub repositories and understand their codebase structure, "
        "decision patterns, and onboarding paths.\n\n"
        "*How to use:*\n"
        "1️⃣ Send me a GitHub repo name: `owner/repo` (e.g., `torvalds/linux`)\n"
        "2️⃣ I'll analyze it and give you insights\n"
        "3️⃣ Ask me questions about the repository\n\n"
        "*Available commands:*\n"
        "/analyze `owner/repo` - Analyze a repository\n"
        "/latest - Get info about the last analyzed repo\n"
        "/decisions - View architectural decisions\n"
        "/busfactor - View bus factor analysis\n"
        "/ghostcode - View unused code findings\n"
        "/onboarding `level` - Get onboarding guide (junior/senior)\n"
        "/help - Show this message\n"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")
    logger.info(f"User {user_id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "*Onboarding Archaeologist Bot Commands*\n\n"
        "*Analysis*\n"
        "`/analyze owner/repo` - Analyze a GitHub repository\n"
        "`/latest` - Get the latest analyzed repository\n\n"
        "*Repository Insights*\n"
        "`/decisions` - View architectural decisions\n"
        "`/busfactor` - Show key person dependencies\n"
        "`/ghostcode` - Find unused/deprecated code\n"
        "`/onboarding junior|senior` - Get onboarding guide\n\n"
        "*General*\n"
        "`/help` - Show this message\n"
        "`/start` - Show welcome message\n\n"
        "*Or just send a message with* `owner/repo` *format!*\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze command"""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Please provide repo name: `/analyze owner/repo`", parse_mode="Markdown")
        return

    repo_input = context.args[0]
    await _handle_repo_analysis(update, context, repo_input)


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /latest command"""
    await update.message.reply_text("🔍 Fetching latest analyzed repository...", parse_mode="Markdown")
    
    try:
        latest = await bot_manager.get_latest_repo()
        if not latest:
            await update.message.reply_text("❌ No repositories analyzed yet.")
            return

        repo_name = f"{latest['owner']}/{latest['repo']}"
        user_id = update.effective_user.id
        user_sessions[user_id] = {"repository_id": latest["repository_id"], "repo_name": repo_name}

        keyboard = [
            [InlineKeyboardButton("📊 Decisions", callback_data="decisions"),
             InlineKeyboardButton("🚌 Bus Factor", callback_data="busfactor")],
            [InlineKeyboardButton("👻 Ghost Code", callback_data="ghostcode"),
             InlineKeyboardButton("🎓 Onboarding", callback_data="onboarding")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"📦 Latest Repository: `{repo_name}`\n\nChoose an analysis:"
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
        logger.error(f"Error in latest_command: {e}")


async def decisions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /decisions command"""
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("repository_id"):
        await update.message.reply_text("❌ No repository loaded. Use `/analyze owner/repo` first.", parse_mode="Markdown")
        return

    await update.message.reply_text("📊 Fetching architectural decisions...", parse_mode="Markdown")

    try:
        decisions = await bot_manager.get_decisions(session["repository_id"])
        text = decisions.get("text", "No decisions found")
        
        # Split long messages
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
        logger.error(f"Error in decisions_command: {e}")


async def busfactor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /busfactor command"""
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("repository_id"):
        await update.message.reply_text("❌ No repository loaded. Use `/analyze owner/repo` first.", parse_mode="Markdown")
        return

    await update.message.reply_text("🚌 Analyzing bus factor...", parse_mode="Markdown")

    try:
        busfactor = await bot_manager.get_bus_factor(session["repository_id"])
        text = busfactor.get("text", "No bus factor findings")
        
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
        logger.error(f"Error in busfactor_command: {e}")


async def ghostcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ghostcode command"""
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("repository_id"):
        await update.message.reply_text("❌ No repository loaded. Use `/analyze owner/repo` first.", parse_mode="Markdown")
        return

    await update.message.reply_text("👻 Detecting ghost code...", parse_mode="Markdown")

    try:
        ghostcode = await bot_manager.get_ghost_code(session["repository_id"])
        text = ghostcode.get("text", "No ghost code found")
        
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
        logger.error(f"Error in ghostcode_command: {e}")


async def onboarding_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /onboarding command"""
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("repository_id"):
        await update.message.reply_text("❌ No repository loaded. Use `/analyze owner/repo` first.", parse_mode="Markdown")
        return

    level = context.args[0] if context.args else "junior"
    if level not in ["junior", "senior"]:
        level = "junior"

    await update.message.reply_text(f"🎓 Generating {level} onboarding guide...", parse_mode="Markdown")

    try:
        onboarding = await bot_manager.get_onboarding_path(session["repository_id"], level)
        text = onboarding.get("text", "No onboarding path found")
        
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
        logger.error(f"Error in onboarding_command: {e}")


# ============================================================================
# Message Handlers
# ============================================================================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages (repo names or questions)"""
    text = update.message.text.strip()

    # Check if it's a repo name (contains /)
    if "/" in text and not text.startswith("/"):
        await _handle_repo_analysis(update, context, text)
    else:
        # Treat as question for current repo
        user_id = update.effective_user.id
        session = user_sessions.get(user_id)

        if not session or not session.get("repository_id"):
            await update.message.reply_text(
                "❌ No repository loaded. Please analyze a repo first:\n"
                "`/analyze owner/repo`\n\n"
                "Or send a repo name like: `owner/repo`",
                parse_mode="Markdown"
            )
            return

        await _handle_question(update, context, session["repository_id"], text)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions.get(user_id)

    if not session or not session.get("repository_id"):
        await query.answer("❌ Session expired. Use /latest or /analyze again.", show_alert=True)
        return

    await query.answer()

    if query.data == "decisions":
        await query.edit_message_text("📊 Fetching architectural decisions...")
        decisions = await bot_manager.get_decisions(session["repository_id"])
        text = decisions.get("text", "No decisions found")
        for chunk in _chunk_message(text):
            await context.bot.send_message(chat_id=query.message.chat_id, text=chunk, parse_mode="Markdown")

    elif query.data == "busfactor":
        await query.edit_message_text("🚌 Analyzing bus factor...")
        busfactor = await bot_manager.get_bus_factor(session["repository_id"])
        text = busfactor.get("text", "No bus factor findings")
        for chunk in _chunk_message(text):
            await context.bot.send_message(chat_id=query.message.chat_id, text=chunk, parse_mode="Markdown")

    elif query.data == "ghostcode":
        await query.edit_message_text("👻 Detecting ghost code...")
        ghostcode = await bot_manager.get_ghost_code(session["repository_id"])
        text = ghostcode.get("text", "No ghost code found")
        for chunk in _chunk_message(text):
            await context.bot.send_message(chat_id=query.message.chat_id, text=chunk, parse_mode="Markdown")

    elif query.data == "onboarding":
        await query.edit_message_text("🎓 Choose level:\nJunior or Senior?")
        # You could add more buttons here for level selection


# ============================================================================
# Helper Functions
# ============================================================================

async def _handle_repo_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, repo_input: str) -> None:
    """Analyze a repository"""
    parts = repo_input.split("/")
    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Invalid format. Use: `owner/repo` (e.g., `torvalds/linux`)",
            parse_mode="Markdown"
        )
        return

    owner, repo = parts[0].strip(), parts[1].strip()
    user_id = update.effective_user.id

    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    await update.message.reply_text(f"🔍 Analyzing `{owner}/{repo}`... This may take a minute...", parse_mode="Markdown")

    try:
        result = await bot_manager.analyze_repo(owner, repo)
        
        # Store in session
        if "repository_id" in result:
            user_sessions[user_id] = {
                "repository_id": result["repository_id"],
                "repo_name": f"{owner}/{repo}"
            }

        text = result.get("text", "Analysis complete")
        
        # Send results in chunks
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")

        # Send follow-up options
        keyboard = [
            [InlineKeyboardButton("📊 Decisions", callback_data="decisions"),
             InlineKeyboardButton("🚌 Bus Factor", callback_data="busfactor")],
            [InlineKeyboardButton("👻 Ghost Code", callback_data="ghostcode"),
             InlineKeyboardButton("🎓 Onboarding", callback_data="onboarding")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("What would you like to know more about?", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error analyzing repo: {e}")
        await update.message.reply_text(f"❌ Error analyzing repository: {str(e)}", parse_mode="Markdown")


async def _handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE, repo_id: int, question: str) -> None:
    """Answer a question about a repository"""
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    try:
        result = await bot_manager.ask_question(repo_id, question)
        text = result.get("text", "No answer found")
        
        for chunk in _chunk_message(text):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode="Markdown")


def _chunk_message(text: str, max_length: int = 4096) -> list[str]:
    """Split long messages to fit Telegram's limit"""
    chunks = []
    current = ""
    
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            if current:
                chunks.append(current)
            current = line
        else:
            current += "\n" + line if current else line
    
    if current:
        chunks.append(current)
    
    return chunks


# ============================================================================
# Bot Setup
# ============================================================================

def setup_telegram_bot() -> Application:
    """Setup and return the Telegram bot application"""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    application = Application.builder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(CommandHandler("decisions", decisions_command))
    application.add_handler(CommandHandler("busfactor", busfactor_command))
    application.add_handler(CommandHandler("ghostcode", ghostcode_command))
    application.add_handler(CommandHandler("onboarding", onboarding_command))

    # Message handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    logger.info("Telegram bot setup complete")
    return application


async def start_bot():
    """Start the bot with polling"""
    app = setup_telegram_bot()
    
    logger.info(f"Starting Telegram bot in {ENVIRONMENT} mode...")
    if ENVIRONMENT == "production":
        logger.info(f"Using webhook mode (expected to be called via FastAPI)")
    else:
        logger.info("Using polling mode (local development)")
        await app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())