import asyncio
import os
from dotenv import load_dotenv
from splinter import Browser

load_dotenv()

username = os.getenv('USR')
password = os.getenv('PWD')
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'}
base_url = 'https://www.ebay-kleinanzeigen.de/'
login_url = "https://www.ebay-kleinanzeigen.de/m-einloggen.html?targetUrl=/"
article_url = ""
contact_msg = f'Guten Tag,\nich bin zur Zeit auf der Suche nach einer Wohnung und bin auf Ihre Anzeige gestoßen.\n \
                    Kurz ein wenig zu mir: Ich bin ein ruhiger, ordentlicher Typ, 31 Jahre alt und befinde mich gerade \
                    in einer Umschulung zum Fachinformatiker. Für mein Homeoffice suche ich darum eine passende Wohnung \
                    und würde gerne eine Besichtigung vereinbaren. Unter der Woche habe ich ab 17:00 Uhr Zeit, am \
                    Wochenende bin ich flexibler.\nIch würde mich über eine Antwort sehr freuen.\nLieben Gruß, Marius'

async def send_msg_on_ebay():
    browser = Browser('firefox')
    #browser.driver.execute_cdp_cmd('Network.setUserAgentOverride', headers)
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

asyncio.run(send_msg_on_ebay())
