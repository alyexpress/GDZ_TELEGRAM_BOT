from bs4 import BeautifulSoup
import requests

from config import ITEMS, SITES, DEBUG

def get_urls(name:str, num:str, _num:str=None):
    site = SITES[ITEMS[name]["site"]]
    url = ITEMS[name]["url"].replace("****", num)
    if _num: url = url.replace("***", _num)
    response = requests.get(url)
    if response.status_code == 403:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    if site['type'] == "img":
        imgs = []
        for img in soup.find_all("img", alt=True):
            if DEBUG: print(img)
            if (img['alt'].startswith(site['alt'] if type(site['alt']) is str else tuple(site['alt']))
                and img['alt'].endswith(ITEMS[name].get('ed', '')) and img['src'].startswith(site.get('src', ''))):
                imgs.append(site['prefix'] + img['src'])
        if DEBUG: print(imgs)
        return imgs
    elif site['type'] == "text":
        if DEBUG: print(soup.text)
        try:
            text = soup.text.split(site['_text'])[1].split(site['text_'])[0]
            text = site['start'] + text.split(site['start'])[1]
            text = text.replace(site['remove'], "")
            while "\n\n" in text: text = text.replace("\n\n", "\n")
            return text, url
        except: return "", url