import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from sympy import sympify

# Cấu hình log gọn
logging.basicConfig(format="%(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

# Lưu tổng theo group
group_totals = {}

# Danh sách group for bot allowedusing 
ALLOWED_GROUPS = {
    -1003957978195,
}

# Chỉ only 1 user bot accept message
ALLOWED_USER = 1573531032  # <-- replace your user

# Regex kiểm tra phép toán
VALID_EXPR = re.compile(r'^[0-9\+\-\*\/\.\s]+$')

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    expr = update.message.text.strip()

    if chat_id not in ALLOWED_GROUPS:
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

    response = f"before: {before}\nnow: {expr} = {now}\ntotal: {total}"

    # Log ra console
    logging.info(f"[Group {chat_id}] User {user_id} | {response.replace(chr(10), ' | ')}")

    # Gửi kết quả vào group
    await update.message.reply_text(response)

# Lệnh /myid để lấy user_id và chat_id
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"👤 user_id: {user_id}\n💬 chat_id: {chat_id}")

def main():
    TOKEN = "8810034885:AAFmYj9AIIAlaC2ZZXCaQn4ihwaEDeE_LRI"  # <-- token bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Lệnh /myid
    app.add_handler(CommandHandler("myid", myid))

    # Chỉ xử lý text phép toán
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    app.run_polling()

if __name__ == "__main__":
    main()
