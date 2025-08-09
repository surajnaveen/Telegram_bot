import os
import uuid
import qrcode
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Application, MessageHandler, filters, ContextTypes, ConversationHandler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

WAITING_FOR_TEXT, AFTER_GENERATE = range(2)

#qr generte function
def generate_qr_code(input_text):
    img = qrcode.make(input_text)
    filename = f"qr_code_{uuid.uuid4()}.png"
    img.save(filename)
    return filename

#Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your QR code bot. Send me a link or text, and I will generate a QR code for you. To generate qr code please use /generate command.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send me a link or text to generate a QR code.")
    return WAITING_FOR_TEXT

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Generating QR code for:\n {user_text}...")

    qr_filename = generate_qr_code(user_text)

    with open(qr_filename, "rb") as photo:
        await update.message.reply_photo(photo)
    
    os.remove(qr_filename)
    await update.message.reply_text("QR code generation complete. If you want to generate again, use /generate.")
    return ConversationHandler.END

async def after_generate_respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("QR code generation complete. If you want to generate again, use /generate.")

#     #Take the confirmation
#     user_confirmation = update.message.text.lower()
#     if user_confirmation == 'yes':
#         await update.message.reply_text("QR code is generating...")
#     elif user_confirmation == 'no':
#         await update.message.reply_text("QR code generation cancelled.")
#     else:
#         await update.message.reply_text("Please reply with 'yes' or 'no'.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("QR code generation cancelled. if you want to start over, use /generate.")
    return ConversationHandler.END


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={
            WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            AFTER_GENERATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, after_generate_respond)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling(poll_interval=2)