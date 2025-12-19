import os
import logging
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

# ========== الإعدادات ==========
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = "@FullSolutions_bot"

# استجابات مخصصة
CUSTOM_RESPONSES = {
    "ابي واحد يعرف لمادة": "اي اعرف لها وش عندك",
    "احد يحل واجب": "طيب بحل لك وش واجبك",
    "ابغى واحد يحل": "طيب بحل لك",
    "ابي واحد يسوي لي مشروع": "طيب بسوي لك",
}

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== معالجات الأوامر ==========
def start_command(update: Update, context: CallbackContext):
    """معالج أمر /start"""
    user = update.effective_user
    update.message.reply_text(f"مرحباً {user.first_name}! 👋\nأنا بوت الحلول الكاملة.")

def handle_group_message(update: Update, context: CallbackContext):
    """معالج رسائل المجموعات"""
    try:
        message_text = update.message.text.strip()
        user = update.message.from_user
        
        logger.info(f"رسالة من @{user.username}: {message_text}")
        
        # التحقق من أي من العبارات موجودة في النص
        for key in CUSTOM_RESPONSES:
            if key in message_text:
                try:
                    # محاولة إرسال رسالة خاصة
                    context.bot.send_message(
                        chat_id=user.id,
                        text=f"📨 *رد من بوت الحلول الكاملة*\n\n{CUSTOM_RESPONSES[key]}\n\n_يمكنك التواصل معي مباشرة هنا_",
                        parse_mode='Markdown'
                    )
                    
                    # تأكيد في المجموعة
                    update.message.reply_text(f"✅ @{user.username}\nتم إرسال الرد لك في الرسائل الخاصة 📩")
                    
                    logger.info(f"تم إرسال رد إلى @{user.username}")
                    
                except Exception as e:
                    logger.error(f"خطأ: {e}")
                    update.message.reply_text(
                        f"🔒 @{user.username}\n\nيرجى البدء مع البوت أولاً:\n@{BOT_USERNAME}"
                    )
                break
        
    except Exception as e:
        logger.error(f"خطأ في معالجة رسالة: {e}")

def error_handler(update: Update, context: CallbackContext):
    """معالجة الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")

def main():
    """الدالة الرئيسية"""
    # التحقق من وجود التوكن
    if not TOKEN:
        logger.error("❌ لم يتم تعيين TELEGRAM_BOT_TOKEN!")
        return
    
    logger.info("🚀 بدء تشغيل بوت الحلول الكاملة...")
    
    try:
        # إنشاء Updater
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # إضافة المعالجات
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(MessageHandler(
            Filters.text & Filters.chat_type.groups,
            handle_group_message
        ))
        
        dispatcher.add_error_handler(error_handler)
        
        # بدء البوت
        updater.start_polling()
        logger.info("✅ البوت يعمل الآن...")
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")

if __name__ == "__main__":
    main()
