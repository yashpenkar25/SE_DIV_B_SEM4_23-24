import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import pyshorteners
import time
from requests.exceptions import ReadTimeout

shorter = pyshorteners.Shortener()

def shorten_url(url):
    max_retries = 3
    retry_delay = 1  # in seconds
    for attempt in range(max_retries):
        try:
            shortened_url = shorter.tinyurl.short(url)
            return shortened_url
        except ReadTimeout as e:
            print(f"Timeout error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    print("Failed to shorten URL after multiple attempts.")
    return None

# Generating URL
def generate_url(part1, part2, search_for, ch):
    url = part1
    list1 = list(search_for)
    l = len(list1)
    for i in range(0, l):
        if list1[i] == ' ':
            list1[i] = ch
        url = url + list1[i]
    url = url + part2
    return url

def start(search_for):
    logo = '''\n  ░█▀▀░█░░░▀█▀░█▀█░█░█░█▀█░█▀▄░▀█▀░░░█░█░█▀▀░░░█▀█░█▄█░█▀█░▀▀█░█▀█░█▀█\n  ░█▀▀░█░░░░█░░█▀▀░█▀▄░█▀█░█▀▄░░█░░░░▀▄▀░▀▀█░░░█▀█░█░█░█▀█░▄▀░░█░█░█░█\n  ░▀░░░▀▀▀░▀▀▀░▀░░░▀░▀░▀░▀░▀░▀░░▀░░░░░▀░░▀▀▀░░░▀░▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀░▀\n    '''
    print(logo)

    amazon_url = generate_url('https://www.amazon.in/s?k=', '&ref=nb_sb_noss_1', search_for, '+')
    sn_url = generate_url('https://www.snapdeal.com/search?keyword=', '&sort=rlvncy', search_for, '%20')
    fk_url = generate_url('https://www.flipkart.com/search?q=', '&otracker=search', search_for, '%20')

    headers = {
        "Host": "www.amazon.in",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    headers2 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
                "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r1 = requests.get(amazon_url, headers=headers)
    r2 = requests.get(sn_url, headers=headers2)
    content2 = r2.content
    content = r1.content

    if r1.status_code != 200 or r2.status_code != 200:
        print('Sorry cannot fetch data for this product right now!!')
        exit()

    soup2 = BeautifulSoup(content2, "html.parser")
    soup1 = BeautifulSoup(content, "html.parser")

    data = {
        "Sold By": [],
        "Product Info": [],
        "Price": [],
        "Link To Site": []
    }

    # Scraping Amazon
    cnt = 0
    for t in soup1.find_all('span', attrs={'class': 'a-size-medium a-color-base a-text-normal'}, text=True):
        data["Sold By"].append('Amazon')
        data["Product Info"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break
    if len(data["Sold By"]) == 0:
        for t in soup1.find_all('span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}, text=True):
            data["Sold By"].append('Amazon')
            data["Product Info"].append(t.get_text())
            cnt += 1
            if cnt == 5:
                break

    cnt = 0
    for t in soup1.find_all('span', attrs={'class': 'a-price-whole'}, text=True):
        data["Price"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break
    cnt = 0
    for t in soup1.find_all('a', attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal',
                                        'href': re.compile("^https://www.amazon.in/")}, href=True):
        long_link = f"https://www.amazon.in{t.get('href')}"
        data["Link To Site"].append(shorten_url(f'{long_link}'))
        cnt += 1
        if cnt == 5:
            break

    # Scraping Snapdeal
    cnt = 0
    for t in soup2.find_all('p', attrs={'class': 'product-title'}, text=True):
        data["Sold By"].append('Snapdeal')
        data["Product Info"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break

    cnt = 0
    for t in soup2.find_all('span', attrs={'class': 'product-price'}, text=True):
        data["Price"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break

    cnt = 0
    for t in soup2.find_all('a', attrs={'class': 'dp-widget-link noUdLine', 'href': re.compile("^https://www.snapdeal.com/")}, href=True):
        long_link = t.get('href')
        data["Link To Site"].append(shorten_url(f'{long_link}'))
        cnt += 1
        if cnt == 5:
            break

    # Scraping Flipkart
    headers3 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
                "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r3 = requests.get(fk_url, headers=headers3)
    content3 = r3.content

    if r3.status_code != 200:
        print('Sorry cannot fetch data for this product right now!!')
        exit()

    soup3 = BeautifulSoup(content3, "html.parser")

    cnt = 0
    for t in soup3.find_all('div', attrs={'class': '_4rR01T'}, text=True):
        data["Sold By"].append('Flipkart')
        data["Product Info"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break

    cnt = 0
    for t in soup3.find_all('div', attrs={'class': '_30jeq3 _1_WHN1'}, text=True):
        data["Price"].append(t.get_text())
        cnt += 1
        if cnt == 5:
            break

    cnt = 0
    for t in soup3.find_all('a', attrs={'class': '_1fQZEK', 'href': re.compile("^https://www.flipkart.com/")}, href=True):
        long_link = f"https://www.flipkart.com{t.get('href')}"
        data["Link To Site"].append(shorten_url(f'{long_link}'))
        cnt += 1
        if cnt == 5:
            break

    df = pd.DataFrame(data=data)
    return df
