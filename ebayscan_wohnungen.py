import asyncio
import requests
import os
import time
#import schedule
import telegram
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from splinter import Browser


async def sendmsg(message_text):
    #await bot.send_message(chat_id=chat_id, text=message_text, disable_web_page_preview=True)
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML', disable_web_page_preview=True)

async def sendphotos(media):
    await bot.send_media_group(chat_id=chat_id, media=media)


def find_photos(entry):
    entry_url = f'https://www.ebay-kleinanzeigen.de/{entry.find("a", class_="ellipsis")["href"]}'
    response = sess.get(entry_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    photos = [img.get('src') for img in soup.find_all('img', attrs={'id': 'viewad-image'})]
    return photos


def set_entry_attributes(entry):
    entry_dict = {
        "title": entry.find('a', class_='ellipsis').text.strip(),
        "price": entry.find('p', class_='aditem-main--middle--price-shipping--price').text.strip(),
        "location": ' '.join(entry.find('div', class_='aditem-main--top--left').text.split()),
        "url": f'https://www.ebay-kleinanzeigen.de/{entry.find("a", class_="ellipsis")["href"]}',
        "photo": entry.find('div', class_='aditem-image').find('div', class_='imagebox srpimagebox')['data-imgsrc']
    }
    return entry_dict


async def scan_and_notify():
    global latest_entry
    response = sess.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('article', class_='aditem')
    new_entry = listings[0]
    photos = find_photos(new_entry)
    if new_entry:
        entry = set_entry_attributes(new_entry)
        media = [telegram.InputMediaPhoto(photo_url) for photo_url in photos]
        if new_entry != latest_entry:
            latest_entry = new_entry
            message = '<a href="{0}">{1}</a>'.format(entry["url"], entry["title"])
            await sendmsg(f'NEW LISTING:\n{message}\n{entry["location"]}  Preis: {entry["price"]}')
            await sendphotos(media)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f'Next scan in: {timer}', end="\r")
        time.sleep(1)
        t -= 1

async def main():
    # Schedule the scan to run every 10 minutes
    #schedule.every(10).minutes.do(scan_and_notify)
    # Start the scheduler loop
    while True:
        #schedule.run_pending()
        await scan_and_notify()
        countdown(600)


load_dotenv()

username = os.getenv('USR')
password = os.getenv('PWD')

tg_api_key = os.getenv('TG_API_KEY')
chat_id = os.getenv('TG_CHAT_ID')

url = "https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/kassel/anzeige:angebote/preis:200:350/c203l4922r30"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/58.0.3029.110 Safari/537.3'}

sess = requests.session()
bot = telegram.Bot(token=tg_api_key)

latest_entry = None

asyncio.run(main())


# ~~~~~~~~~~~~~~~~~~~~~~ DEVELOPMENT
login_url = "https://www.ebay-kleinanzeigen.de/m-einloggen.html?targetUrl=/"
article_url = ""
contact_msg = f'Guten Tag,\nich bin zur Zeit auf der Suche nach einer Wohnung und bin auf Ihre Anzeige gestoßen.\n \
                    Kurz ein wenig zu mir: Ich bin ein ruhiger, ordentlicher Typ, 31 Jahre alt und befinde mich gerade \
                    in einer Umschulung zum Fachinformatiker. Für mein Homeoffice suche ich darum eine passende Wohnung \
                    und würde gerne eine Besichtigung vereinbaren. Unter der Woche habe ich ab 17:00 Uhr Zeit, am \
                    Wochenende bin ich flexibler.\nIch würde mich über eine Antwort sehr freuen.\nLieben Gruß, Marius'

async def send_msg_on_ebay():
    browser = Browser('chrome')
    browser.visit(login_url)
    browser.driver.maximize_window()
    await asyncio.sleep(1)

    browser.find_by_name('login-email').fill(username)
    browser.find_by_name('login-password').fill(password)
    browser.find_by_name('recaptcha-anchor').check()
    browser.find_by_xpath("//button[@type='submit']").click()
    await asyncio.sleep(10)
    """
    if browser.is_text_present('Nachricht schreiben'):
        #print('Login successful')
        await sendmsg('Login successful')
    else:
        #print('Login failed')
        await sendmsg('Login failed')

    browser.visit(action)
    """
    #print(f'Action: {acmsg}')
    #await sendmsg(f'Action: {acmsg}')
    await asyncio.sleep(1)