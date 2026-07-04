import logging
import os
import re
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

# Your Telegram user ID
ALLOWED_USER = 1573531032

# Allow only numbers and math operators
VALID_EXPR = re.compile(r'^[0-9+\-*/.\s]+$')


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Read text or caption
    if update.message.text:
        expr = update.message.text.strip()
    elif update.message.caption:
        expr = update.message.caption.strip()
    else:
        return

    # Allow only you
    if user_id != ALLOWED_USER:
        return

    # Ignore invalid expressions
    if not VALID_EXPR.match(expr):
        return

    before = group_totals.get(chat_id, 0)

    try:
        now = float(sympify(expr))
    except Exception:
        return

    total = before + now
    group_totals[chat_id] = total

    await update.message.reply_text(
        f"before: {before}\n"
        f"now: {expr} = {now}\n"
        f"total: {total}"
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

    # Accept text, photo captions, video captions and document captions
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
