import os
import logging
import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from telegram.error import Forbidden

# ========== الإعدادات ==========
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = "FullSolutions_bot"

# تحقق من وجود التوكن
if not TOKEN:
    print("❌ خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN في متغيرات البيئة!")
    print("📋 خطوات الحل:")
    print("1. اذهب إلى https://dashboard.render.com")
    print("2. اختر خدمتك 'fullsolutions-bot'")
    print("3. اضغط على تبويب Environment")
    print("4. أضف متغير البيئة:")
    print("   Key: TELEGRAM_BOT_TOKEN")
    print("   Value: توكن_بوتك_هنا")
    print("5. اضغط Save وأعد التشغيل")
    sys.exit(1)

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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    user = update.effective_user
    await update.message.reply_text(f"مرحباً {user.first_name}! 👋\nأنا بوت الحلول الكاملة.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    help_text = """
📚 *كيفية استخدام البوت:*
1. أضف البوت إلى مجموعتك
2. اكتب إحدى العبارات:
   • ابي واحد يعرف لمادة
   • احد يحل واجب
   • ابغى واحد يحل
   • ابي واحد يسوي لي مشروع

سيرد عليك البوت في الخاص تلقائياً!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج رسائل المجموعات"""
    try:
        # تأكد أن الرسالة في مجموعة
        if update.message.chat.type not in ['group', 'supergroup']:
            return
        
        message_text = update.message.text.strip()
        user = update.message.from_user
        
        logger.info(f"رسالة من @{user.username}: {message_text}")
        
        # البحث عن عبارات مطابقة
        for key in CUSTOM_RESPONSES:
            if key in message_text:
                try:
                    # إرسال رسالة خاصة
                    await context.bot.send_message(
                        chat_id=user.id,
                        text=f"📨 *رد من بوت الحلول الكاملة*\n\n{CUSTOM_RESPONSES[key]}\n\n_يمكنك التواصل معي مباشرة هنا_",
                        parse_mode='Markdown'
                    )
                    
                    # تأكيد في المجموعة
                    await update.message.reply_text(
                        f"✅ @{user.username}\nتم إرسال الرد لك في الرسائل الخاصة 📩"
                    )
                    
                    logger.info(f"تم إرسال رد إلى @{user.username}")
                    
                except Forbidden:
                    # المستخدم حظر البوت
                    await update.message.reply_text(
                        f"🔒 @{user.username}\n\n"
                        f"عذراً، لا يمكنني إرسال رسالة خاصة لك.\n"
                        f"يرجى البدء مع البوت أولاً: @{BOT_USERNAME}"
                    )
                    logger.warning(f"لا يمكن إرسال رسالة خاصة إلى @{user.username}")
                    
                except Exception as e:
                    logger.error(f"خطأ في إرسال رسالة: {e}")
                    await update.message.reply_text(
                        f"@{user.username} حدث خطأ، يرجى المحاولة مرة أخرى."
                    )
                
                break  # التوقف بعد أول تطابق
        
    except Exception as e:
        logger.error(f"خطأ في معالجة رسالة المجموعة: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")

def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الحلول الكاملة...")
    logger.info(f"✅ التوكن مضبوط: {'نعم' if TOKEN else 'لا'}")
    
    try:
        # إنشاء التطبيق
        application = Application.builder().token(TOKEN).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.GROUPS,
            handle_group_message
        ))
        
        application.add_error_handler(error_handler)
        
        # بدء البوت
        logger.info("✅ البوت يعمل في وضع Polling...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")
        raise

if __name__ == "__main__":
    main()
