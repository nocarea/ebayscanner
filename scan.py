import asyncio
import requests
import os
import sys
import time
import telegram
import configparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv

"""
ARGUMENTS:
1 = USERNAME
2 = CHAT ID
3 = SEARCH
4 = MIN PRICE
5 = MAX PRICE
6 = LOCATION
7 = RADIUS (5, 10, 20, 30, 50, 100, 150, 200)
"""

load_dotenv()

tg_api_key = os.getenv('TG_API_KEY_JAMES')
bot = telegram.Bot(token=tg_api_key)
sess = requests.session()
config = configparser.ConfigParser()
base_url = "https://www.ebay-kleinanzeigen.de"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


user = sys.argv[1]
chat_id = sys.argv[2]
bot_profile = sys.argv[3]
bot_profile_file = f'./Users/{user}/Profiles/{bot_profile}.ini'

config.read(bot_profile_file)
search_term = config.get(bot_profile, 'search_term')
price_min = config.get(bot_profile, 'price_min')
price_max = config.get(bot_profile, 'price_max')
location = config.get(bot_profile, 'location')
radius = config.get(bot_profile, 'radius')


def process_args():
    global startmsg
    global url
    global filename
    if not os.path.exists(f'./Users/{user}/Logs/'):
        os.makedirs(f'./Users/{user}/Logs/')
    filename = f'./Users/{user}/Logs/{bot_profile}.txt'
    startmsg = f'USER: {user}, ID: {chat_id}\nSEARCH: {search_term}\nPRICE: {price_min}-{price_max}€\nLOCATION: {location}\nRADIUS: +{radius}km'
    url = (
        f'{base_url}/s-suchanfrage.html?'
        f'keywords={search_term}&'
        f'locationStr={location}&'
        f'radius={radius}&'
        f'sortingField=SORTING_DATE&'
        f'pageNum=1&'
        f'action=find&'
        f'maxPrice={price_max}&'
        f'minPrice={price_min}&'
        f'buyNowEnabled=false&'
    )
    print(url)

async def send_message(message_text):
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML', disable_web_page_preview=True)

async def send_nopic():
    with open('./Images/nopic.png', 'rb') as f:
        await bot.send_photo(chat_id=chat_id, photo=f)

async def send_photos(media):
    await bot.send_media_group(chat_id=chat_id, media=media, parse_mode='HTML')

def find_photos(entry):
    entry_url = f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    response = sess.get(entry_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    photos = [img.get('src') for img in soup.find_all('img', attrs={'id': 'viewad-image'})]
    return photos[:3]

def set_entry_attributes(entry):
    entry_dict = {
        "title": entry.find('a', class_='ellipsis').text.strip(),
        "price": entry.find('p', class_='aditem-main--middle--price-shipping--price').text.strip(),
        "location": ' '.join(entry.find('div', class_='aditem-main--top--left').text.split()),
        "adid": entry['data-adid'],
        "url": f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    }
    return entry_dict

async def scan_and_notify():
    with open(filename, 'a+') as f:
        f.seek(0)
        posted_ids = [line.strip() for line in f.readlines()]
        response = sess.get(url, headers=headers, timeout=30.0)
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('article', class_='aditem')
        if listings:
            new_entry = listings[0]
            photos = find_photos(new_entry)
            if new_entry:
                entry = set_entry_attributes(new_entry)
                if entry["adid"] not in posted_ids:
                    f.write(entry["adid"] + '\n')
                    message = '<a href="{0}">{1}</a>'.format(entry["url"], entry["title"])
                    await send_message(f'NEW LISTING:\n{message}\n{entry["location"]}  Preis: {entry["price"]}')
                    if photos == []:
                        await send_nopic()
                    else:
                        """
                        media = []
                        for i, photo_url in enumerate(photos):
                            if i == 0:
                                media.append(telegram.InputMediaPhoto(photo_url, caption=fcaption))
                            else:
                                media.append(telegram.InputMediaPhoto(photo_url))
                        """
                        media = [telegram.InputMediaPhoto(photo_url) for photo_url in photos]
                        await send_photos(media)
        else:
            pass

def countdown(t):
    while t > 0:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f'Next scan in: {timer}', end="\r")
        time.sleep(1)
        t -= 1

async def main():
    while True:
        await scan_and_notify()
        countdown(600)

if __name__ == "__main__":
    process_args()
    print(startmsg)
    asyncio.run(main())

"""
~~~~~~~ to do ~~~~~~~

catch this error and retry:
    raise ReadTimeout(e, request=request)
    requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='www.ebay-kleinanzeigen.de', port=443): Read timed out. (read timeout=30.0)
"""