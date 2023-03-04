import os
import time
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


SEARCH, LOCATION, RADIUS, PRICEMIN, PRICEMAX, RUNBOT, PROFILEACTION, PROFILEADD, PROFILEDELETE, PROFILETOGGLE = range(10)


async def set_variables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user
    global chat_id
    global profile_file
    user = update.message.from_user.first_name.capitalize()
    chat_id = update.message.chat_id
    profile_file = f'./Profiles/{chat_id}-{user}.ini'


def markup(keyboard, placeholder):
    markup = ReplyKeyboardMarkup(keyboard,
                                one_time_keyboard=True,
                                resize_keyboard=True, 
                                input_field_placeholder=placeholder)
    return markup

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GLOBAL COMMANDS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await set_variables(update, context)
    await update.message.reply_text(
        f"🔅  {user}!\n\
    What's up my man!\n\
    You came to the right place.\n\
    Here's a list of available commands:\n"
        "/setup\n\
    Set up a new search agent.\n\
    I will guide you through the process.\n\
    It is recommended to enter a minimum \n\
    and maximum price to avoid getting\n\
    irrelevant results. (Like Laptop Cables\n\
    while looking for Laptops)\n"
        "/profiles\n\
    Manage your search profiles.\n\
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
        "STOP IT"
    )
    return ConversationHandler.END


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SETUP COMMANDS
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await set_variables(update, context)
    if not os.path.exists(f'./Logs/{chat_id}-{user}/'):
        os.makedirs(f'./Logs/{chat_id}-{user}/')
    await update.message.reply_text(
        f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🔅  Let\'s set up a new search agent.  🔅\n\
〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️'
    )
    await update.message.reply_text(
        "📍  Enter a Location to search in  📍\n\
        (   name and/or zipcode   )\n\
        (skip to search everywhere)",
    reply_markup=markup([["skip"]], "Location")
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
            reply_markup=markup([["skip"]], "Search Term"))
        return SEARCH
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
⭕️              Select Search Radius (km)              ⭕️\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=markup([["0", "5", "10"], ["20", "30", "50"], ["100", "150", "200"]], "Radius"))
        return RADIUS

async def set_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global radius
    radius = update.message.text
    if radius.isdigit():
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔎     What would you like to search for?    🔍\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
        reply_markup=markup([["skip"]], "Search Term"))
        return SEARCH
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
    ⭕️              Select Search Radius (km)              ⭕️\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=markup([["0", "5", "10"], ["20", "30", "50"], ["100", "150", "200"]], "Radius"))
        return RADIUS



async def set_search_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global search_term
    search_term = update.message.text.title()
    await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔻              Enter minimum Price              🔻\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
        reply_markup=markup([["skip"]], "Minimum Price"))
    return PRICEMIN


async def set_pricemin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_min
    price_min = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_min = update.message.text
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔺              Enter maximum Price              🔺\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=markup([["skip"]], "Maximum Price"))
        return PRICEMAX
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔻          Digits only. Enter minimum Price         🔻\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=markup([["skip"]], "Minimum Price"))
        return PRICEMIN


async def set_pricemax(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global price_max
    price_max = ""
    if update.message.text.isdigit() or update.message.text == "skip":
        if update.message.text.isdigit():
            price_max = update.message.text
        await update.message.reply_text(
        f'''🔅 Profile added:
        ➖➖➖➖➖➖➖➖➖
        Search Term: {search_term.title()}
        Location: {location.title()}
        Radius: +{radius}km
        Price Range: {price_min}-{price_max}€
        ➖➖➖➖➖➖➖➖➖'''
        )
        await profile_add(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(f'〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\
🔺          Digits only. Enter maximum Price:         🔺\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️',
            reply_markup=markup([["skip"]], "Maximum Price"))
        return PRICEMAX


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PROFILE COMMANDS
async def profile_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await set_variables(update, context)
    config.read(profile_file)
    if not config.sections():
        await update.message.reply_text(
            "You don't have any Search Profiles yet.\nTo create a profile, type /setup")
    else:
        await update.message.reply_text("Your Profiles:")
        for i, profile in enumerate(config.sections()):
            values = dict(config[profile])
            active_status = "                  active  🟢" if values['active'] == "1" else "               inactive  🔴"
            message = (
            f"<code>Profile {i+1}</code>{active_status}\n"
            f"<s>---------------------------------------------</s>\n"
            f"Search Term: <b>{values['search_term'].title()}</b>\n"
            f"Location: <b>{values['location'].title()} (+{values['radius']}km)</b>\n"
            f"Price Range: <b>{values['price_min']}-{values['price_max']}€</b>")
            await update.message.reply_text(message, parse_mode='HTML')
        await update.message.reply_text(
            "Choose an action.\n"
            "Or click here: /cancel to cancel",
            reply_markup=markup([["Activate/Deactivate a Profile"], ["Delete a Profile"]], "Choose"))
        return PROFILEACTION



async def profile_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    config.read(profile_file)
    keyboard = [[]]
    for i, profile in enumerate(config.sections()):
        keyboard[0].append(f'Profile {i+1}')
    if update.message.text == "Activate/Deactivate a Profile":
        await update.message.reply_text("Which Profile would you like to switch on/off?",
                reply_markup=markup(keyboard, "Choose"))
        return PROFILETOGGLE
    elif update.message.text == "Delete a Profile":
        await update.message.reply_text("Which Profile would you like to delete?",
                reply_markup=markup(keyboard, "Choose"))
        return PROFILEDELETE
    else:
        await update.message.reply_text("???")
        return ConversationHandler.END
    

async def profile_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_variables(update, context)
    config.read(profile_file)
    profiles = config.sections()
    answer = update.message.text[-1]
    if answer.isdigit(): 
        profile_index = int(answer) - 1
        logfile = f'./Logs/{chat_id}-{user}/{profiles[profile_index]}.txt'
        if os.path.exists(logfile):
            os.remove(logfile)
        config.remove_section(profiles[profile_index])
        with open(profile_file, 'w') as configfile:
            config.write(configfile)
        await update.message.reply_text(f'Deleted Profile {profile_index + 1}, (back to /profiles -click)')
        return ConversationHandler.END
    else:
        await update.message.reply_text("Thats not a valid input.")
        return ConversationHandler.END


async def profile_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_variables(update, context)
    config.read(profile_file)
    answer = update.message.text[-1]
    if answer.isdigit():
        profile_index = int(answer) - 1
        profile = config.sections()[profile_index]
        active_status = config[profile]['active']
        if active_status == "1":
            value = "inactive"
            config.set(profile, 'active', "0")
        else:
            value = "active"
            config.set(profile, 'active', "1")
        #if config.sections()[profile_index]['active'] == '1':
        #config.set(config.sections()[profile_index], 'active', '0')
        with open(profile_file, 'w') as configfile:
            config.write(configfile)
        await update.message.reply_text(f'Set Profile {profile_index + 1} to {value}, (back to /profiles <-click)')
        return ConversationHandler.END
    else:
        await update.message.reply_text("Thats not a valid input.")
        return PROFILEACTION


async def profile_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_variables(update, context)
    bot_profile = f'{search_term.title()}-{location.title()}-{radius}-{price_min}-{price_max}'
    config.read(profile_file)
    config[bot_profile] = {
        'active': 1,
        'user': user,
        'chat_id': chat_id,
        'search_term': search_term,
        'price_min': price_min,
        'price_max': price_max,
        'location': location,
        'radius': radius
        }
    with open(profile_file, 'w') as configfile:
        config.write(configfile)
    logfile = f'./Logs/{chat_id}-{user}/{bot_profile}.txt'
    with open(logfile, 'w') as log:
        log.write("")

        

def main() -> None:
    try:
        application = Application.builder().token(tg_api_token).build()
        conv_handler = ConversationHandler(
            entry_points = [
                        CommandHandler("start", start),
                        CommandHandler("setup", setup),
                        CommandHandler("profiles", profile_list),
                        CommandHandler("help", help),
            ],
            states = {
                    SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_search_term)],
                    LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_location)],
                    RADIUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_radius)],
                    PRICEMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemin)],
                    PRICEMAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_pricemax)],
                    PROFILEACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_action)],
                    PROFILEADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_add)],
                    PROFILEDELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_delete)],
                    PROFILETOGGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_toggle)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conv_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    except Exception as e:
        print(f'Error: {str(e)}')
        time.sleep(30)
        main()


if __name__ == "__main__":
    main()



# run all active profiles
