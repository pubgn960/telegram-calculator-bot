import logging
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from sympy import sympify

logging.basicConfig(format="%(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

group_totals = {}
ALLOWED_USER = 1573531032
VALID_EXPR = re.compile(r'^[0-9\+\-\*\/\.\s]+$')

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if update.message.text:
    expr = update.message.text.strip()
elif update.message.caption:
    expr = update.message.caption.strip()
else:
    return

    if user_id != ALLOWED_USER:
        return
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
        f"before: {before}\nnow: {expr} = {now}\ntotal: {total}"
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👤 user_id: {update.effective_user.id}\n💬 chat_id: {update.effective_chat.id}"
    )

def main():
    TOKEN = os.getenv("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("myid", myid))
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
