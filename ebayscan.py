import asyncio
import requests
import os
import sys
import time
import telegram
from bs4 import BeautifulSoup
from dotenv import load_dotenv

"""
ARGUMENTS:
1 = USER
2 = SEARCH
3 = MIN PRICE
4 = MAX PRICE
5 = LOCATION
6 = RADIUS (5, 10, 20, 30, 50, 100, 150, 200)
"""

load_dotenv()

tg_api_key = os.getenv('TG_API_KEY')
bot = telegram.Bot(token=tg_api_key)
sess = requests.session()
base_url = "https://www.ebay-kleinanzeigen.de/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def handle_args():
    global startmsg
    global chat_id
    global search_term
    global chat_id
    global url
    global filename
    if len(sys.argv) >= 4:
        price_min = sys.argv[3]
        price_max = sys.argv[4]
        location = sys.argv[5]
        radius = sys.argv[6]        
    else:
        price_min = ""
        price_max = ""
        location = ""
        radius = 0
    chat_id = sys.argv[1]
    search_term = sys.argv[2]
    if not os.path.exists(f'./Logs/{chat_id}'):
        os.makedirs(f'./Logs/{chat_id}')
    filename = f'./Logs/{chat_id}/{search_term.lower()}_{price_min}_{price_max}.txt'
    startmsg = f'USER ID: {chat_id}\nSEARCH: {search_term}\nPRICE: {price_min}-{price_max}€\nLOCATION: {location.capitalize()}\nRADIUS: +{radius}km'
    url = f'{base_url}s-suchanfrage.html?keywords={search_term}&categoryId=&locationStr={location.lower()}&locationId=&radius={radius}\
                &sortingField=SORTING_DATE&adType=&posterType=&pageNum=1&action=find&maxPrice={price_max}&minPrice={price_min}\
                                                                                        &buyNowEnabled=false&shippingCarrier='
    #print(url)

async def sendmsg(message_text):
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML', disable_web_page_preview=True)

async def sendnopic():
    with open('./Images/nopic.png', 'rb') as f:
        await bot.send_photo(chat_id=chat_id, photo=f)

async def sendphotos(media):
    await bot.send_media_group(chat_id=chat_id, media=media)

def find_photos(entry):
    entry_url = f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    response = sess.get(entry_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    photos = [img.get('src') for img in soup.find_all('img', attrs={'id': 'viewad-image'})]
    return photos[:5]

def set_entry_attributes(entry):
    entry_dict = {
        "title": entry.find('a', class_='ellipsis').text.strip(),
        "price": entry.find('p', class_='aditem-main--middle--price-shipping--price').text.strip(),
        "location": ' '.join(entry.find('div', class_='aditem-main--top--left').text.split()),
        "url": f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    }
    return entry_dict

async def scan_and_notify():
    global latest_entry
    with open(filename, 'a+') as f:
        f.seek(0)
        posted_urls = [line.strip() for line in f.readlines()]
        response = sess.get(url, headers=headers, timeout=30.0)
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('article', class_='aditem')
        if listings:
            new_entry = listings[0]
            photos = find_photos(new_entry)
            if new_entry:
                entry = set_entry_attributes(new_entry)
                if entry["url"] not in posted_urls:
                    f.write(entry["url"] + '\n')
                    latest_entry = entry["url"]
                    message = '<a href="{0}">{1}</a>'.format(entry["url"], entry["title"])
                    await sendmsg(f'NEW LISTING:\n{message}\n{entry["location"]}  Preis: {entry["price"]}')
                    if photos == []:
                        await sendnopic()
                    else:
                        media = [telegram.InputMediaPhoto(photo_url) for photo_url in photos]
                        await sendphotos(media)
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
    handle_args()
    print(startmsg)
    asyncio.run(main())
