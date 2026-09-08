# Telegram AI-бот на Gemini

Минимальный Telegram-бот, который отвечает через Google Gemini и готов к деплою на Railway.

## Локальный запуск

1. Создай бота через [@BotFather](https://t.me/BotFather) и скопируй токен.
2. Получи ключ Gemini в [Google AI Studio](https://aistudio.google.com/apikey).
3. Скопируй `.env.example` в `.env` и заполни `TELEGRAM_TOKEN` и `GEMINI_API_KEY`.
4. Установи зависимости и запусти:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Деплой на Railway

1. Загрузи этот репозиторий на GitHub.
2. В Railway выбери **New Project** -> **Deploy from GitHub repo**.
3. В настройках сервиса добавь переменные `TELEGRAM_TOKEN` и `GEMINI_API_KEY`.
4. Нажми **Deploy**. Railway сам использует `Dockerfile`.

Ключи не добавляй в GitHub. История диалога хранится в памяти процесса и сбрасывается после перезапуска.

Важно: у Railway условия бесплатного использования меняются и могут требовать подтверждение оплаты или кредитов. Gemini также имеет квоты бесплатного уровня, которые зависят от модели и аккаунта.