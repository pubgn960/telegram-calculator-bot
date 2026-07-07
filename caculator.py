import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from sympy import sympify

logging.basicConfig(format="%(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

# Running total for each group
group_totals = {}

# Your Telegram User ID
ALLOWED_USERS = [
    1573531032,
    6656261222,
    1408137192
]


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id != ALLOWED_USER:
        return

    # Read text or caption
    if update.message.text:
        content = update.message.text
    elif update.message.caption:
        content = update.message.caption
    else:
        return

    before = group_totals.get(chat_id, 0)

    # If user sends only 0, show remaining amount
    if content.strip() == "0":
        await update.message.reply_text(
            f"💰 Remaining Amount: {before}"
        )
        return

    now = 0

    # Read every line separately
    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            value = float(sympify(line))
            now += value
        except Exception:
            # Ignore text lines
            continue

    if now == 0:
        return

    total = before + now
    group_totals[chat_id] = total

    await update.message.reply_text(
        f"before: {before}\n"
        f"now: {now}\n"
        f"total: {total}"
    )


async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id != ALLOWED_USER:
        return

    previous = group_totals.get(chat_id, 0)
    group_totals[chat_id] = 0

    await update.message.reply_text(
        f"✅ Payment Received\n\n"
        f"Paid Amount: {previous}\n"
        f"Remaining Amount: 0"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👤 user_id: {update.effective_user.id}\n"
        f"💬 chat_id: {update.effective_chat.id}"
    )


def main():
    TOKEN = os.getenv("TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("paid", paid))

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL)
            & ~filters.COMMAND,
            calculate,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
