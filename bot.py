import logging
import random
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== تنظیمات ====================
TOKEN = os.environ.get("8857616173:AAH9GFlfd8GLHjkoUf3elLCO9u05XA-EPvE")  # توکن ربات رو توی Render به عنوان Environment Variable بذار
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # اگه نداری خالی بمونه
PORT = int(os.environ.get("PORT", 10000))
RENDER_URL = os.environ.get("https://bot-clean-xqxg.onrender.com")  # مثلاً https://your-bot.onrender.com

# ==================== بارگذاری فحش‌های آماده ====================
with open("insults.json", "r", encoding="utf-8") as f:
    insults_db = json.load(f)

# ==================== Gemini (اگر کلید داشت) ====================
use_gemini = bool(GEMINI_API_KEY)
if use_gemini:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

# ==================== توابع کمکی ====================
def generate_ai_insult(name: str, style: str = "خلاقانه و خنده‌دار و اصلاً توهین‌آمیز نباشه") -> str:
    """با Gemini یه فحش شخصی‌سازی‌شده می‌سازه"""
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
    """یه قالب تصادفی انتخاب می‌کنه و اسم رو جایگزین می‌کنه"""
    text = random.choice(templates)
    return text.replace("{name}", name) if name else text

# ==================== دستورات ربات ====================
async def fohsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فحش معمولی یا شخصی‌سازی‌شده"""
    target = None
    if context.args:
        target = context.args[0]  # @username

    insult = None
    if target and use_gemini:
        insult = generate_ai_insult(target, "فحش کاملاً خنده‌دار و غیرتوهین‌آمیز")
    if not insult:
        insult = get_random_template(insults_db["single"], name=target if target else "کاربر")
    await update.message.reply_text(insult)

async def tamjid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعریف در قالب فحش"""
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
    """جنگ دو نفر و فحش دادن به هر دو"""
    if len(context.args) < 2:
        await update.message.reply_text("دو تا یوزرنیم رو وارد کن. مثال:\n/dava @Ali @Reza")
        return
    user1, user2 = context.args[0], context.args[1]
    intro = random.choice(insults_db["dava_intro"]).format(user1=user1, user2=user2)
    insult1 = None
    insult2 = None
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
    """لطیفه‌ای که آخرش یه فحش خلاقانه داره"""
    joke = get_random_template(insults_db["latife"])
    await update.message.reply_text(joke)

# ==================== اجرای ربات با webhook ====================
def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    if not TOKEN or not RENDER_URL:
        raise ValueError("لطفاً TOKEN و RENDER_URL رو توی Environment Variables تنظیم کن.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("fohsh", fohsh))
    app.add_handler(CommandHandler("tamjid", tamjid))
    app.add_handler(CommandHandler("dava", dava))
    app.add_handler(CommandHandler("latife", latife))

    # تنظیم webhook
    webhook_url = f"{RENDER_URL}/webhook"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=webhook_url
    )
    print(f"✅ ربات روی پورت {PORT} با webhook روشن شد...")

if __name__ == "__main__":
    main()