import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram.error import Forbidden, NetworkError

# ========== الإعدادات ==========
# الحصول على التوكن من متغيرات البيئة (آمن)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = "FullSolutions_bot"  # بدون @

# استجابات مخصصة
CUSTOM_RESPONSES = {
    "ابي واحد يعرف لمادة": "اي اعرف لها وش عندك",
    "احد يحل واجب": "طيب بحل لك وش واجبك",
    "ابغى واحد يحل": "طيب بحل لك",
    "ابي واحد يسوي لي مشروع": "طيب بسوي لك",
    "مرحبا": "مرحباً بك! كيف يمكنني مساعدتك؟",
    "شكرا": "العفو! إذا احتجت مساعدة ثانية أنا هنا",
}

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== معالجات الأوامر ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    user = update.effective_user
    welcome_text = f"""
مرحباً {user.first_name}! 👋

أنا بوت *الحلول الكاملة* 🤖
يمكنني مساعدتك في:
• حل الواجبات
• المشاريع الدراسية
• شرح المواد

*كيفية الاستخدام:*
1. أضفني إلى مجموعتك
2. اكتب إحدى العبارات التالية:
   - ابي واحد يعرف لمادة
   - احد يحل واجب
   - ابغى واحد يحل
   - ابي واحد يسوي لي مشروع

سيقوم البوت بالرد عليك في الخاص تلقائياً! 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    help_text = """
*📚 قائمة الأوامر المتاحة:*

/start - بدء استخدام البوت
/help - عرض هذه المساعدة
/about - معلومات عن البوت
/contact - للتواصل مع المطور

*💬 كيفية العمل:*
1. أضف البوت إلى مجموعتك
2. اكتب إحدى العبارات التالية في المجموعة:
   • "ابي واحد يعرف لمادة"
   • "احد يحل واجب"
   • "ابغى واحد يحل"
   • "ابي واحد يسوي لي مشروع"

سيرد عليك البوت في الخاص تلقائياً!

*🔧 إذا لم تصل الرسالة:*
تأكد أنك بدأت محادثة مع البوت أولاً
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /about"""
    about_text = """
*🤖 عن بوت الحلول الكاملة*

*الإصدار:* 2.0
*المطور:* Full Solutions Team
*الوصف:* بوت مساعد للطلاب لحل الواجبات والمشاريع الدراسية

*المميزات:*
✓ ردود تلقائية في المجموعات
✓ دعم متعدد اللغات
✓ تشغيل مستمر 24/7
✓ استجابات سريعة

تابعنا للتحديثات الجديدة! 🚀
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ========== معالج رسائل المجموعات ==========
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج رسائل المجموعات"""
    try:
        # التأكد من أن الرسالة في مجموعة
        if update.message.chat.type not in ['group', 'supergroup']:
            return
        
        message_text = update.message.text.strip()
        user = update.message.from_user
        
        logger.info(f"رسالة من @{user.username} في مجموعة {update.message.chat.id}: {message_text}")
        
        # البحث عن عبارات مطابقة
        for key in CUSTOM_RESPONSES:
            if key.lower() in message_text.lower():
                try:
                    # محاولة إرسال رسالة خاصة
                    await context.bot.send_message(
                        chat_id=user.id,
                        text=f"📨 *رد من بوت الحلول الكاملة*\n\n{CUSTOM_RESPONSES[key]}\n\n_يمكنك التواصل معي مباشرة هنا_",
                        parse_mode='Markdown'
                    )
                    
                    # تأكيد في المجموعة
                    confirmation = f"""
✅ @{user.username}

تم إرسال الرد لك في الرسائل الخاصة 📩
إذا لم تصل الرسالة، تأكد من:
1. بدأت محادثة مع @{BOT_USERNAME}
2. المسموح بالرسائل الخاصة
"""
                    await update.message.reply_text(confirmation)
                    
                    logger.info(f"تم إرسال رد إلى @{user.username}")
                    
                except Forbidden:
                    # المستخدم حظر البوت أو لم يبدأ محادثة
                    error_msg = f"""
🔒 @{user.username}

عذراً، لا يمكنني إرسال رسالة خاصة لك.
يرجى:
1. البدء مع البوت: @{BOT_USERNAME}
2. الضغط على /start
3. إعادة المحاولة
"""
                    await update.message.reply_text(error_msg)
                    logger.warning(f"لا يمكن إرسال رسالة خاصة إلى @{user.username}")
                    
                except Exception as e:
                    logger.error(f"خطأ في إرسال رسالة: {e}")
                    await update.message.reply_text(
                        f"@{user.username} حدث خطأ، يرجى المحاولة مرة أخرى لاحقاً."
                    )
                
                break  # التوقف بعد أول تطابق
        
    except Exception as e:
        logger.error(f"خطأ في معالجة رسالة المجموعة: {e}")

# ========== معالج الأخطاء ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء العامة"""
    try:
        logger.error(f"حدث خطأ أثناء معالجة التحديث: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقاً."
            )
    except:
        pass

# ========== وظائف التشغيل ==========
async def setup_webhook(application, webhook_url):
    """إعداد Webhook للاستضافة"""
    await application.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    logger.info(f"تم إعداد Webhook على: {webhook_url}")

async def start_polling(application):
    """بدء Polling (للاختبار المحلي)"""
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("✅ البوت يعمل في وضع Polling...")

def main():
    """الدالة الرئيسية"""
    # التحقق من وجود التوكن
    if not TOKEN:
        logger.error("❌ لم يتم تعيين TELEGRAM_BOT_TOKEN في متغيرات البيئة!")
        logger.error("يرجى إضافة التوكن كمتغير بيئة")
        return
    
    logger.info("🚀 بدء تشغيل بوت الحلول الكاملة...")
    
    try:
        # إنشاء التطبيق
        application = Application.builder().token(TOKEN).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.GROUPS,
            handle_group_message
        ))
        
        application.add_error_handler(error_handler)
        
        # التحقق من وضع التشغيل
        webhook_url = os.environ.get('WEBHOOK_URL')
        
        if webhook_url:
            # وضع Webhook (للاستضافة)
            logger.info("🌐 تشغيل في وضع Webhook...")
            asyncio.run(setup_webhook(application, webhook_url))
            
            # للحفاظ على التشغيل المستمر
            import time
            while True:
                time.sleep(86400)  # النوم ليوم كامل
        else:
            # وضع Polling (للاختبار المحلي)
            logger.info("🔍 تشغيل في وضع Polling...")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")
        raise

if __name__ == "__main__":
    main()