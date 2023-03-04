import asyncio
import requests
import os
import time
import telegram
import configparser

from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv()

tg_api_key_p2 = os.getenv('TG_API_KEY_JAMES')

bot = telegram.Bot(token=tg_api_key_p2)
sess = requests.session()
config = configparser.ConfigParser()

async def send_message(chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML', disable_web_page_preview=True)

async def send_nopic(chat_id):
    with open('./Images/nopic.png', 'rb') as f:
        await bot.send_photo(chat_id=chat_id, photo=f)

async def send_photos(chat_id, media):
    await bot.send_media_group(chat_id=chat_id, media=media, parse_mode='HTML')


base_url = "https://www.ebay-kleinanzeigen.de"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


async def scan_and_notify():
    active_profiles = scan_profiles()
    for profile in active_profiles:
        chat_id = profile[0]
        logfile = f'./Logs/{profile[0]}-{profile[1]}/{profile[2]}.txt'
        with open(logfile, 'a+') as f:
            f.seek(0)
            posted_ids = [line.strip() for line in f.readlines()]
            response = sess.get(profile[3], headers=headers, timeout=30.0)
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('article', class_='aditem')
            if listings:
                new_entry = listings[0]
                photos = find_photos(new_entry)
                entry = set_entry_attributes(new_entry)
                if entry["adid"] not in posted_ids:
                    f.write(entry["adid"] + '\n')
                    message = f'<a href="{entry["url"]}">{entry["title"]}</a>'
                    await send_message(chat_id, 
                        f'🔅                NEW LISTING                 🔅\n'
                        f'{message}\n{entry["location"]}  Price: {entry["price"]}')
                    if photos == []:
                        await send_nopic(chat_id)
                    else:
                        media = [telegram.InputMediaPhoto(photo_url) for photo_url in photos]
                        await send_photos(chat_id, media)
            else:
                pass


def scan_profiles():
    global active
    profile_files = []
    for profile_file in os.listdir('./Profiles/'):
        if os.path.isfile(os.path.join('./Profiles/', profile_file)):
            profile_files.append(f'./Profiles/{profile_file}')
    active_profiles = []
    for profile_file in profile_files:
        config.clear()
        config.read(profile_file)
        for profile in config.sections():
            if config[profile]['active'] == "1":
                chat_id = config.get(profile, 'chat_id')
                user = config.get(profile, 'user')
                search_term = config.get(profile, 'search_term')
                price_min = config.get(profile, 'price_min')
                price_max = config.get(profile, 'price_max')
                location = config.get(profile, 'location')
                radius = config.get(profile, 'radius')
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
                active_profiles.append([chat_id, user, profile, url])
                #print(f'{len(active_profiles)}, {profile}, {user}')
    active = len(active_profiles)
    return active_profiles


def set_entry_attributes(entry):
    entry_dict = {
        "title": entry.find('a', class_='ellipsis').text.strip(),
        "price": entry.find('p', class_='aditem-main--middle--price-shipping--price').text.strip(),
        "location": ' '.join(entry.find('div', class_='aditem-main--top--left').text.split()),
        "adid": entry['data-adid'],
        "url": f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    }
    return entry_dict


def find_photos(entry):
    entry_url = f'{base_url}{entry.find("a", class_="ellipsis")["href"]}'
    response = sess.get(entry_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    photos = [img.get('src') for img in soup.find_all('img', attrs={'id': 'viewad-image'})]
    return photos[:3]


def countdown(t):
    while t > 0:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f'Active Profiles: {active}, Next scan in: {timer}', end="\r")
        time.sleep(1)
        t -= 1

async def main():
    while True:
        await scan_and_notify()
        countdown(600)

if __name__ == "__main__":
    asyncio.run(main())
