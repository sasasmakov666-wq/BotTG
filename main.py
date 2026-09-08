import asyncio
import logging
import os
from collections import defaultdict, deque

from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("8820369455:AAFRMi7zxWfGQ5nVLbe7ERlgEiOz2jYx0Pg")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6LNfQOvOryREwwIywILo9KB3KYO2Smr2xvcktyP-tlhLw")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Ты полезный AI-ассистент. Отвечай на русском языке, если пользователь не попросил другой язык.",
)

if not TELEGRAM_TOKEN:
    raise RuntimeError("Не задана переменная TELEGRAM_TOKEN")
if not GEMINI_API_KEY:
    raise RuntimeError("Не задана переменная GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
chat_history: dict[int, deque[tuple[str, str]]] = defaultdict(lambda: deque(maxlen=12))


def build_prompt(chat_id: int, user_text: str) -> str:
    history = chat_history[chat_id]
    messages = [f"Инструкция: {SYSTEM_PROMPT}", ""]
    for role, text in history:
        messages.append(f"{role}: {text}")
    messages.append(f"Пользователь: {user_text}")
    messages.append("Ассистент:")
    return "\n".join(messages)


def ask_gemini(prompt: str) -> str:
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    answer = response.text
    if not answer:
        raise RuntimeError("Gemini вернул пустой ответ")
    return answer.strip()


async def reply_in_chunks(update: Update, text: str) -> None:
    for start_index in range(0, len(text), 4000):
        await update.message.reply_text(text[start_index : start_index + 4000])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    await update.message.reply_text(
        "Привет! Я AI-бот на Gemini. Напиши вопрос, и я постараюсь помочь.\n\n"
        "Команды: /start, /help, /clear"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    await update.message.reply_text(
        "Просто отправь мне сообщение.\n"
        "/clear — очистить историю текущего диалога."
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    chat_history[update.effective_chat.id].clear()
    await update.message.reply_text("История диалога очищена.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()
    prompt = build_prompt(chat_id, user_text)

    await update.message.chat.send_action(ChatAction.TYPING)
    try:
        answer = await asyncio.to_thread(ask_gemini, prompt)
    except Exception:
        logger.exception("Ошибка при запросе к Gemini")
        await update.message.reply_text(
            "Не удалось получить ответ от Gemini. Проверь ключ API или попробуй еще раз позже."
        )
        return

    chat_history[chat_id].append(("Пользователь", user_text))
    chat_history[chat_id].append(("Ассистент", answer))
    await reply_in_chunks(update, answer)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен с моделью %s", GEMINI_MODEL)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()