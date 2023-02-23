import os
from dotenv import load_dotenv
import subprocess
import telegram
load_dotenv()

tg_api_token = os.getenv('TG_API_KEY')
bot = telegram.Bot(token=tg_api_token)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

SEARCH, LOCATION, RADIUS, PRICEMIN, PRICEMAX, RUNBOT = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Let's set up a search agent for you.\n"
        "Please enter your search term.\n",
        )
    return SEARCH

async def set_search_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global chat_id
    global search_term
    chat_id = update.message.chat_id
    search_term = update.message.text
    await update.message.reply_text(
        "Enter location"
        )
    return LOCATION

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global user
    global location
    user = update.message.from_user
    location = update.message.text.replace(" ", "-")
    keyboard = [[InlineKeyboardButton("None", callback_data="3")],
            [InlineKeyboardButton("+5km", callback_data="35"),
            InlineKeyboardButton("+10km", callback_data="310"),
            InlineKeyboardButton("+20km", callback_data="320"),
            InlineKeyboardButton("+30km", callback_data="330")],
            [InlineKeyboardButton("+50km", callback_data="350"),
            InlineKeyboardButton("+100km", callback_data="3100"),
            InlineKeyboardButton("+150km", callback_data="3150"),
            InlineKeyboardButton("+200km", callback_data="3200")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    return RADIUS

async def set_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    radius = ""
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    globals()["radius"] = query.data[1:]
    await bot.send_message(chat_id=chat_id, text="Enter min price")
    return PRICEMIN

async def set_pricemin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_min
    if update.message.text.isdigit():
        price_min = update.message.text
        await update.message.reply_text("Enter max price:")
        return PRICEMAX
    else:
        await update.message.reply_text("Only digits allowed, start over")
        return ConversationHandler.END

async def set_pricemax(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_max
    if update.message.text.isdigit():
        price_max = update.message.text
        await update.message.reply_text("Alright, let's start your bot.")
        await run_bot(update, context)


async def run_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global price_max
    if update.message.text.isdigit():
        price_max = update.message.text
        await update.message.reply_text(
        f'Search term: {search_term}\n\
        Location: {location}\n\
        Radius: {radius}\n\
        Price range: {price_min} - {price_max}€'
        )
        # Specify the path to the Python script you want to run
        script_path = "/home/marius/code/ebay_scan/development/ebayscan.py"
        # Use the subprocess module to open a new terminal window and run the Python script
        subprocess.Popen(["gnome-terminal", "--", "python3", script_path, str(chat_id), (search_term), (price_min), (price_max), (location), (radius)])
    else:
        await update.message.reply_text("Only digits allowed, start over")
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Canceled")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(tg_api_token).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SEARCH: [MessageHandler(filters.TEXT, set_search_term)],
            LOCATION: [MessageHandler(filters.TEXT, set_location)],
            RADIUS: [CallbackQueryHandler(set_radius)],
            PRICEMIN: [MessageHandler(filters.TEXT, set_pricemin)],
            PRICEMAX: [MessageHandler(filters.TEXT, set_pricemax)],
            RUNBOT: [MessageHandler(filters.TEXT, run_bot)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
