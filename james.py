import os
import subprocess
import telegram
import configparser
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

tg_api_token = os.getenv('TG_API_KEY_JAMES')
bot = telegram.Bot(token=tg_api_token)
config = configparser.ConfigParser()
reply_keyboard = [["skip"]]


SEARCH, LOCATION, RADIUS, PRICEMIN, PRICEMAX, RUNBOT = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global user
    global chat_id
    user = update.message.from_user.first_name.capitalize()
    chat_id = update.message.chat_id
    await update.message.reply_text(
        f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔅  Let\'s set up a search agent, {user}  🔅\n'
        "       Please enter your search term.\n"
        "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"
    )
    return SEARCH


async def set_search_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global search_term
    search_term = update.message.text.title()
    await update.message.reply_text(
        f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🕹              Enter a Location              🕹\n'
        "               (name and/or zipcode)\n"
        "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Location"
    ))
    return LOCATION

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    global location
    location = update.message.text
    if location == "skip":
        radius = "0"
        location = ""
        await update.message.reply_text(
            f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔻              Enter minimum Price:              🔻\n'
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Minimum Price"
        ))
        return PRICEMIN
    else:
        radius_keyboard = [[telegram.KeyboardButton("0"), telegram.KeyboardButton("5"), telegram.KeyboardButton("10")],
                        [telegram.KeyboardButton("20"), telegram.KeyboardButton("30"), telegram.KeyboardButton("50")],
                        [telegram.KeyboardButton("100"), telegram.KeyboardButton("150"), telegram.KeyboardButton("200")]]
        await update.message.reply_text(
            f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n⭕️              Select Search Radius (km):              ⭕️\n'
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            reply_markup=ReplyKeyboardMarkup(radius_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Radius"
        ))
        return RADIUS

async def set_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    radius = update.message.text
    await update.message.reply_text(
        f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔻              Enter minimum Price:              🔻\n'
        "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Minimum Price"
    ))
    return PRICEMIN

async def set_pricemin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_min
    price_min = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_min = update.message.text
        await update.message.reply_text(
            f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔺              Enter maximum Price:              🔺\n'
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Minimum Price"
        ))
        return PRICEMAX
    else:
        await update.message.reply_text(
            f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔻          Digits only. Enter minimum Price:         🔻\n'
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Minimum Price"
        ))
        return PRICEMIN

async def set_pricemax(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_max
    price_max = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_max = update.message.text
        await update.message.reply_text(
        f'''
        ➖➖➖➖➖➖➖➖➖
        Search Term: {search_term.title()}
        Location: -{location}
        Radius: +{radius}km
        Price Range: {price_min}-{price_max}€
        ➖➖➖➖➖➖➖➖➖'''
        )
        run_bot()
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔺          Digits only. Enter maximum Price:         🔺\n'
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Minimum Price"
        ))
        return PRICEMAX


def run_bot() -> int:
    bot_profile = f'{search_term.title()}-{location.title()}-{price_min}-{price_max}'
    if not os.path.exists(f'./Users/{user}/Profiles/'):
        os.makedirs(f'./Users/{user}/Profiles/')
    filename = f'./Users/{user}/Profiles/{bot_profile}.ini'
    config[bot_profile] = {
        'search_term': search_term,
        'price_min': price_min,
        'price_max': price_max,
        'location': location,
        'radius': radius
        }
    with open(filename, 'w') as configfile:
        config.write(configfile)
    script_path = "./scan.py"
    subprocess.Popen(["gnome-terminal", "--", "python3", script_path, (user), str(chat_id), (bot_profile)])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Canceled")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(tg_api_token).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_search_term)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_location)],
            RADIUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_radius)],
            PRICEMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemin)],
            PRICEMAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemax)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

# list, add, remove, activate, deactivate profiles
"""
keyboard = [[InlineKeyboardButton("None", callback_data="0")],
        [InlineKeyboardButton("+5km", callback_data="5"),
        InlineKeyboardButton("+10km", callback_data="10"),
        InlineKeyboardButton("+20km", callback_data="20"),
        InlineKeyboardButton("+30km", callback_data="0")],
        [InlineKeyboardButton("+50km", callback_data="50"),
        InlineKeyboardButton("+100km", callback_data="100"),
        InlineKeyboardButton("+150km", callback_data="150"),
        InlineKeyboardButton("+200km", callback_data="200")]]
reply_markup = InlineKeyboardMarkup(keyboard)
"""