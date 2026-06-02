import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask
import threading

BOT_TOKEN = "AAH090LSVmMcpbA9hiArXBMUzVl3iUDXIDQ"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🔵 گیت‌هاب", url="https://github.com"), InlineKeyboardButton("📢 تلگرام", url="https://t.me/telegram")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help"), InlineKeyboardButton("👋 سلام", callback_data="hello")],
        [InlineKeyboardButton("🎲 عدد تصادفی", callback_data="random"), InlineKeyboardButton("📊 آمار", callback_data="stats")]
    ]
    await update.message.reply_html(f"👋 سلام {user.mention_html()}!\n\n🐍 ربات پایتونی روی Render!\n☁️ اجرای ۲۴/۷ رایگان\n\n🦜 هر چی بگی رو اکو می‌کنم!", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 /start - منو\n/help - راهنما\n/about - درباره", parse_mode="HTML")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ربات پایتونی روی Render ☁️\nاجرای ۲۴/۷ | رایگان", parse_mode="HTML")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user.first_name
    keyboard = [[InlineKeyboardButton("🔄 اکو دوباره", callback_data=f"echo:{text}")], [InlineKeyboardButton("🏠 منو", callback_data="menu")]]
    await update.message.reply_text(f"🦜 اکو از {user}:\n\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))

async def echo_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_sticker(update.message.sticker.file_id)

async def echo_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    await update.message.reply_photo(photo, caption=update.message.caption or "📸 عکس تو!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user.first_name
    if data == "help": await query.edit_message_text(f"ℹ️ {user}، کافیه پیام بدی تا اکو کنم!")
    elif data == "hello": await query.edit_message_text(f"👋 سلام {user}! ✨")
    elif data == "random":
        import random; await query.edit_message_text(f"🎲 {random.randint(1,100)}")
    elif data == "stats": await query.edit_message_text(f"📊 پایتون روی Render ☁️\n👤 {user}")
    elif data.startswith("echo:"): await query.edit_message_text(f"🔄 اکو:\n{data.split(':',1)[1]}")
    elif data == "menu": await query.edit_message_text("🏠 /start رو بزن")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Sticker.ALL, echo_sticker))
    app.add_handler(MessageHandler(filters.PHOTO, echo_photo))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    flask_app = Flask(__name__)
    @flask_app.route('/')
    def home():
        return "<h1>🐍☁️ ربات آنلاینه!</h1>"
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    logger.info("🤖 ربات شروع شد!")
    app.run_polling()

if __name__ == "__main__":
    main()