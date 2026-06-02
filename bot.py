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

# ==================== دستورات اصلی ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 گیت‌هاب", url="https://github.com/aghoali/bot-clean")],
        [InlineKeyboardButton("📢 تلگرام", url="https://t.me/Mew_albot")],
        [InlineKeyboardButton("🤖 چت با هوش مصنوعی", callback_data="ai_info")],
        [InlineKeyboardButton("🔥 فحش بده", callback_data="fohsh_info")],
        [InlineKeyboardButton("😈 تمجید مسخره", callback_data="tamjid_info")],
        [InlineKeyboardButton("⚔️ دعوا", callback_data="dava_info")],
        [InlineKeyboardButton("🤣 لطیفه", callback_data="latife_info")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 به ربات همه‌کاره خوش اومدی! 😼\nچیکار برات انجام بدم؟", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 راهنمای ربات همه‌کاره:\n\n"
        "/ai [سوال] - چت با هوش مصنوعی\n"
        "/fohsh - فحش تصادفی\n"
        "/fohsh @user - فحش به یه نفر\n"
        "/tamjid @user - تعریف مسخره‌آمیز\n"
        "/dava @user1 @user2 - دعوای دو نفر\n"
        "/latife - لطیفه فحش‌دار\n"
        "/about - درباره ربات\n"
        "/start - منوی اصلی"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات همه‌کاره Mew_albot\n"
        "نسخه ۲.۰\n"
        "🔥 قابلیت‌ها: چت با هوش مصنوعی، فحش خلاقانه، لطیفه و کلی سرگرمی\n"
        "ساخته‌شده با پایتون و عشق 😸"
    )

async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_sticker(update.message.sticker.file_id)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(update.message.photo[-1].file_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        await query.edit_message_text(
            "🔥 راهنمای ربات همه‌کاره:\n\n"
            "/ai [سوال] - چت با هوش مصنوعی\n"
            "/fohsh - فحش تصادفی\n"
            "/fohsh @user - فحش به یه نفر\n"
            "/tamjid @user - تعریف مسخره‌آمیز\n"
            "/dava @user1 @user2 - دعوای دو نفر\n"
            "/latife - لطیفه فحش‌دار\n"
            "/about - درباره ربات\n"
            "/start - منوی اصلی"
        )
    elif data == "ai_info":
        await query.edit_message_text(
            "🤖 چت با هوش مصنوعی:\n\n"
            "از دستور /ai استفاده کن و سوالت رو بپرس!\n"
            "مثال:\n"
            "/ai چطوری پولدار شم؟\n"
            "/ai یه جوک بگو\n"
            "/ai برنامه‌نویسی رو از کجا شروع کنم؟\n"
            "/ai چرا آسمون آبیه؟"
        )
    elif data == "fohsh_info":
        await query.edit_message_text(
            "🔥 فحش خلاقانه:\n\n"
            "/fohsh - یه فحش باحال تصادفی\n"
            "/fohsh @user - فحش شخصی‌سازی‌شده\n"
            "/dava @user1 @user2 - دعوای دو نفر"
        )
    elif data == "tamjid_info":
        await query.edit_message_text(
            "😈 تمجید مسخره:\n\n"
            "/tamjid @user - تعریف در قالب فحش\n"
            "مثلاً: /tamjid @Ali"
        )
    elif data == "dava_info":
        await query.edit_message_text(
            "⚔️ دعوای دو نفر:\n\n"
            "/dava @user1 @user2\n"
            "مثلاً: /dava @Ali @Reza\n"
            "ربات هر دوتاشون رو مسخره می‌کنه!"
        )
    elif data == "latife_info":
        await query.edit_message_text(
            "🤣 لطیفه فحش‌دار:\n\n"
            "/latife - یه لطیفه که آخرش یه فحش باحال داره!"
        )

# ==================== چت با هوش مصنوعی ====================
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text(
            "❓ سوالت رو بعد از دستور بنویس!\n"
            "مثال:\n"
            "/ai چرا آسمون آبیه؟\n"
            "/ai بهترین زبان برنامه‌نویسی چیه؟\n"
            "/ai یه جوک بگو"
        )
        return
    
    if not use_gemini:
        await update.message.reply_text("❌ هوش مصنوعی فعال نیست. ادمین باید کلید Gemini رو توی Render تنظیم کنه.")
        return
    
    thinking_msg = await update.message.reply_text("🤔 بذار فکر کنم...")
    
    prompt = f"""
    یه جواب مفید، مختصر و خودمونی به این سوال بده.
    اگه سوال طنزآمیز بود، جواب طنزآمیز بده.
    سوال: {user_text}
    """
    try:
        response = model.generate_content(prompt)
        await thinking_msg.edit_text(response.text.strip())
    except Exception as e:
        await thinking_msg.edit_text(f"❌ خطا در ارتباط با هوش مصنوعی: {e}")

# ==================== دستورات فحش ====================
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
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    # دستورات هوش مصنوعی
    app.add_handler(CommandHandler("ai", ai_chat))

    # دستورات فحش
    app.add_handler(CommandHandler("fohsh", fohsh))
    app.add_handler(CommandHandler("tamjid", tamjid))
    app.add_handler(CommandHandler("dava", dava))
    app.add_handler(CommandHandler("latife", latife))

    # اجرای Flask در thread جداگانه
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("✅ ربات Mew_albot با قابلیت چت هوش مصنوعی و فحش خلاقانه روشن شد...")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())