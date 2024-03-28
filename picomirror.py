from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit
import requests
import re
import shutil

def process_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            url = line.strip()
            pico = extract_pico(url, '.p8.png')
            print(pico)
            save_pico(pico[0], pico[1])

def extract_pico(url, pattern):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    links = soup.find_all('a', href=re.compile(pattern))
    split_url = urlsplit(url)
    shorturl=(split_url.scheme + "://" + split_url.netloc)
    return title,shorturl+links[0].get('href')

def save_pico(title, uri):
    filename = './carts/'+title+".p8.png"
    print("downloading "+uri+" to "+filename)
    response = requests.get(uri, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

process_file('sources.txt')
