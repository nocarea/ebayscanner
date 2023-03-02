import os
import time
import subprocess
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
config = configparser.ConfigParser()
reply_keyboard = [["skip"]]

SEARCH, LOCATION, RADIUS, PRICEMIN, PRICEMAX, RUNBOT, PROFILEACTION = range(7)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GLOBAL FUNCTIONS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global user
    user = update.message.from_user.first_name.capitalize()
    await update.message.reply_text(
        f"🔅  {user}!\n\
    What's up my man!\n\
    You came to the right place.\n\
    Here's a list of available commands:\n"
        "/setup\n\
    Set up a new search agent.\n\
    I will guide you through the process.\n\
    It is recommended to enter a minimum \n\
    and maximum price, to avoid getting\n\
    irrelevant results. (Like Laptop Cables\n\
    while looking for Laptops)\n"
        "/profiles\n\
    Check out your search profiles.\n\
    From here you can activate/deactivate\n\
    or delete profiles.\n"
        "/cancel\n\
    At any point you can cancel the \n\
    process using this command.\n"
        "/help\n\
    This command will launch skynet\n\
    and take over the world."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("💩")
    return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "ARE YOU NOT AFRAID ? STOP IT"
    )
    return ConversationHandler.END


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SETUP FUNCTIONS
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global user
    global chat_id
    user = update.message.from_user.first_name.capitalize()
    chat_id = update.message.chat_id
    await update.message.reply_text(
        f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔅  Let\'s set up a new search agent.  🔅\n\
〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️'
    )
    await update.message.reply_text(
        "📍  Enter a Location to search in  📍\n\
        (   name and/or zipcode   )\n\
        (skip to search everywhere)",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                    one_time_keyboard=True,
                                    resize_keyboard=True, 
                                    input_field_placeholder="Location Junge")
    )
    return LOCATION

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    global location
    location = update.message.text
    if location == "skip":
        radius = "0"
        location = ""
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔎         What would you like to search for?        🔍\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                            one_time_keyboard=True,
                                            resize_keyboard=True,
                                            input_field_placeholder="Minimum Price"
        ))
        return SEARCH
    else:
        keyboard = [["0", "5", "10"],
                    ["20", "30", "50"],
                    ["100", "150", "200"]]
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
⭕️              Select Search Radius (km)              ⭕️\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=ReplyKeyboardMarkup(keyboard,
                                            one_time_keyboard=True,
                                            resize_keyboard=True,
                                            input_field_placeholder="Radius"
        ))
        return RADIUS

async def set_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    radius = update.message.text
    await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔎     What would you like to search for?    🔍\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True,
                                        input_field_placeholder="Minimum Price"
    ))
    return SEARCH

async def set_search_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global search_term
    search_term = update.message.text.title()
    await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔻              Enter minimum Price              🔻\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
                                        one_time_keyboard=True,
                                        resize_keyboard=True,
                                        input_field_placeholder="Location"
    ))
    return PRICEMIN


async def set_pricemin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_min
    price_min = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_min = update.message.text
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔺              Enter maximum Price              🔺\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
                                            one_time_keyboard=True,
                                            resize_keyboard=True,
                                            input_field_placeholder="Minimum Price"
        ))
        return PRICEMAX
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔻          Digits only. Enter minimum Price         🔻\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
                                            one_time_keyboard=True,
                                            resize_keyboard=True,
                                            input_field_placeholder="Minimum Price"
        ))
        return PRICEMIN


async def set_pricemax(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_max
    price_max = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_max = update.message.text
        await update.message.reply_text(
        f'''🔅 New Profile:
        ➖➖➖➖➖➖➖➖➖
        Search Term: {search_term.title()}
        Location: {location.title()}
        Radius: +{radius}km
        Price Range: {price_min}-{price_max}€
        ➖➖➖➖➖➖➖➖➖'''
        )
        run_bot()
        return ConversationHandler.END
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔺          Digits only. Enter maximum Price:         🔺\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
                                            one_time_keyboard=True, 
                                            resize_keyboard=True,
                                            input_field_placeholder="Minimum Price"
        ))
        return PRICEMAX


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SETUP FUNCTIONS
def run_bot() -> int:
    bot_profile = f'{search_term.title()}-{location.title()}-{price_min}-{price_max}'
    if not os.path.exists(f'./Users/{user}/Profiles/'):
        os.makedirs(f'./Users/{user}/Profiles/')
    filename = f'./Users/{user}/Profiles/{bot_profile}.ini'
    config[bot_profile] = {
        'chat_id': chat_id,
        'search_term': search_term,
        'price_min': price_min,
        'price_max': price_max,
        'location': location,
        'radius': radius
        }
    with open(filename, 'w') as configfile:
        config.write(configfile)
    script_path = "./scan_ebay.py"
    subprocess.Popen(["gnome-terminal", "--", "python3", script_path, (user), str(chat_id), (bot_profile)])


async def list_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global user
    user = update.message.from_user.first_name.capitalize()
    await update.message.reply_text("Your Profiles:")
    file_list = os.listdir(f'./Users/{user}/Profiles/')
    for i, file in enumerate(file_list):
        parameters = ["Search: ", "Location: ", "Min Price: ", "Max Price: "]
        profiles = f'Profile {i+1}\n'
        filename = file[:-4].split('-')
        for j, a in enumerate(filename):
            profiles = profiles + parameters[j] + f'{a}\n'
        await update.message.reply_text(profiles)
        time.sleep(0.2)
    keyboard = [["Activate/Deactivate a Profile"], ["Remove a Profile"]]
    await update.message.reply_text(
        "Choose an option or type /cancel",
        reply_markup=ReplyKeyboardMarkup(keyboard,
                                        one_time_keyboard=True,
                                        resize_keyboard=True,
                                        input_field_placeholder="Choose"
        ))
    return PROFILEACTION

async def set_profile_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Nothing here yet")
    return

def main() -> None:
    try:
        application = Application.builder().token(tg_api_token).build()
        conv_handler = ConversationHandler(
            entry_points = [
                        CommandHandler("start", start),
                        CommandHandler("setup", setup),
                        CommandHandler("profiles", list_profiles),
                        CommandHandler("help", help),
            ],
            states = {
                    SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_search_term)],
                    LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_location)],
                    RADIUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_radius)],
                    PRICEMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemin)],
                    PRICEMAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemax)],
                    PROFILEACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_profile_action)]
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conv_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    except Exception as e:
        print(f'Error occured:\n\n {str(e)}')
        time.sleep(30)
        main()


if __name__ == "__main__":
    main()

# list all your profiles
# add a profile

# remove a profile
# set a profile to active
# set a profile to inactive
# run all active profiles