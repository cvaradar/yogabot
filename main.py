import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, ContextTypes
from handlers import generate_response, analyze_image, recognize_speech_from_audio
from dotenv import load_dotenv

# Load environment variables from .env file for secure API keys
load_dotenv("yoga-bot-charu.env")

# Get the Telegram bot token from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Handler for the /start command to welcome the user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Yoga Bot! Send a text, image, or voice to get started."
    )

# Handler for text messages - sends text to GPT for yoga suggestions
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text  # Capture user message
    response = generate_response(user_text)  # Get GPT response
    await update.message.reply_text(response)  # Send response back

# Handler for image uploads - analyzes image using Azure Vision API
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()  # Get photo file
    photo_path = f"{photo_file.file_id}.jpg"  # Local path to save the image
    await photo_file.download_to_drive(photo_path)  # Download image

    image_response = analyze_image(photo_path)  # Analyze using Vision API
    await update.message.reply_text(image_response)  # Reply with result

    os.remove(photo_path)  # Clean up local image file

# Handler for voice inputs - converts voice to text using Speech API
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()  # Get voice file
    voice_path = f"{voice_file.file_id}.ogg"  # Local path to save voice
    await voice_file.download_to_drive(voice_path)  # Download audio

    voice_response = recognize_speech_from_audio(voice_path)  # Transcribe voice
    await update.message.reply_text(voice_response)  # Send GPT response

    os.remove(voice_path)  # Clean up local audio file

# Main function initializes bot and adds handlers for commands and inputs
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()  # Create app

    # Register handlers for start command, text, image, and voice inputs
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Yoga Recommendation Bot is running...")  # Log status
    await app.run_polling()  # Start bot polling for updates

# Entry point of the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())