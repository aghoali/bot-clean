import asyncio
import logging
import random
import json
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ==================== بخش Flask برای جلوگیری از خواب ====================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running..."

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# ==================== تنظیمات ربات ====================
BOT_TOKEN = "8857616173:AAH9GFlfd8GLHjkoUf3elLCO9u05XA-EPvE"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ==================== بارگذاری فحش‌های آماده ====================
try:
    with open("insults.json", "r", encoding="utf-8") as f:
        insults_db = json.load(f)
except FileNotFoundError:
    insults_db = {
        "single": ["{name} مثل یه باگ میمونه؛ همه میدونن وجود داره ولی هیچکی دوستش نداره."],
        "tamjid": ["{name} واقعاً موجود خاصیه… البته خاص به معنای نیازمند به کمک فوری."],
        "latife": ["چرا ربات از این گروه نمیره؟ چون مسدود کردنش هم براش زیادی خوب بود."],
        "dava_intro": ["⚔️ نبرد {user1} و {user2} شروع شد:"]
    }

# ==================== Gemini (اگر کلید داشت) ====================
use_gemini = GEMINI_API_KEY is not None and GEMINI_API_KEY != ""
if use_gemini:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

def generate_ai_insult(name: str, style: str = "خلاقانه و خنده‌دار و اصلاً توهین‌آمیز نباشه") -> str:
    if not use_gemini:
        return None
    prompt = f"""
    یه جمله طنزآمیز و کاملاً دوستانه برای {name} بنویس که به شوخی مسخرش کنه.
    سبک: {style}
    توهین واقعی نباشه، فقط یه شوخی بامزه.
    حداکثر دو جمله.
    مستقیماً خود جمله رو بگو، بدون هیچ توضیح اضافه.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return None

def get_random_template(templates: list, name: str = "") -> str:
    text = random.choice(templates)
    return text.replace("{name}", name) if name else text

# ==================== دستورات اصلی قبلی ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 گیت‌هاب", url="https://github.com/aghoali/bot-clean")],
        [InlineKeyboardButton("📢 تلگرام", url="https://t.me/Mew_albot")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        [InlineKeyboardButton("👋 سلام", callback_data="hello")],
        [InlineKeyboardButton("🎲 عدد تصادفی", callback_data="random")],
        [InlineKeyboardButton("📊 آمار", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! به ربات Mew_albot خوش اومدی. 😼", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("راهنما:\n/start\n/help\n/about\n/echo [متن]\n/fohsh\n/fohsh @user\n/tamjid @user\n/dava @user1 @user2\n/latife")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات Mew_albot – ساخته‌شده با عشق و پایتون. 😸")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    keyboard = [[InlineKeyboardButton("🔄 اکو دوباره", callback_data=f"echo_{user_text}")]]
    await update.message.reply_text(user_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_sticker(update.message.sticker.file_id)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(update.message.photo[-1].file_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        await query.edit_message_text("راهنما:\n/start\n/help\n/about\n/echo\n/fohsh\n/tamjid\n/dava\n/latife")
    elif data == "hello":
        await query.edit_message_text("سلام به تو! 😸")
    elif data == "random":
        await query.edit_message_text(f"عدد تصادفی: {random.randint(1, 100)}")
    elif data == "stats":
        await query.edit_message_text("آمار ربات:\nزنده است. فحش می‌دهد. شاد است. 🤖")
    elif data.startswith("echo_"):
        text = data[5:]
        await query.edit_message_text(f"اکو: {text}")
    elif data == "menu":
        await start(update, context)

# ==================== دستورات فحش جدید ====================
async def fohsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = None
    if context.args:
        target = context.args[0]
    insult = None
    if target and use_gemini:
        insult = generate_ai_insult(target, "فحش کاملاً خنده‌دار و غیرتوهین‌آمیز")
    if not insult:
        insult = get_random_template(insults_db["single"], name=target if target else "کاربر")
    await update.message.reply_text(insult)

async def tamjid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = "کاربر"
    if context.args:
        target = context.args[0]
    insult = None
    if target != "کاربر" and use_gemini:
        insult = generate_ai_insult(target, "تعریف کن ولی طوری که انگار داری مسخره‌اش می‌کنی. خیلی بامزه.")
    if not insult:
        insult = get_random_template(insults_db["tamjid"], name=target)
    await update.message.reply_text(insult)

async def dava(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("دو تا یوزرنیم رو وارد کن. مثال:\n/dava @Ali @Reza")
        return
    user1, user2 = context.args[0], context.args[1]
    intro = random.choice(insults_db["dava_intro"]).format(user1=user1, user2=user2)
    insult1 = insult2 = None
    if use_gemini:
        insult1 = generate_ai_insult(user1, "فحش خنده‌دار در قالب یک مبارزه فرضی")
        insult2 = generate_ai_insult(user2, "فحش خنده‌دار در قالب یک مبارزه فرضی")
    if not insult1:
        insult1 = get_random_template(insults_db["single"], name=user1)
    if not insult2:
        insult2 = get_random_template(insults_db["single"], name=user2)
    await update.message.reply_text(
        f"{intro}\n\n"
        f"👈 {user1}: {insult1}\n"
        f"👉 {user2}: {insult2}\n\n"
        f"🤝 نتیجه: هر دوتون در حد هم هستید."
    )

async def latife(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = get_random_template(insults_db["latife"])
    await update.message.reply_text(joke)

# ==================== اجرای ربات ====================
async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    app = Application.builder().token(BOT_TOKEN).build()

    # دستورات اصلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    # دستورات فحش جدید
    app.add_handler(CommandHandler("fohsh", fohsh))
    app.add_handler(CommandHandler("tamjid", tamjid))
    app.add_handler(CommandHandler("dava", dava))
    app.add_handler(CommandHandler("latife", latife))

    # اجرای Flask در thread جداگانه برای جلوگیری از خواب
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("✅ ربات Mew_albot با قابلیت فحش خلاقانه روشن شد...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())