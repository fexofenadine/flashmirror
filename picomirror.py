from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit
import requests
import re
import shutil
import string

def process_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            url = line.strip()
            pico = extract_pico(url, '.p8.png')
            #print(pico)
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
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in title if c in valid_chars)
    #filename = filename.replace(' ','_') # I don't like spaces in filenames.
    filename = './carts/'+filename+".p8.png"
    print("Downloading \""+title+"\" from "+uri+" to "+filename)
    response = requests.get(uri, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

process_file('sources.txt')
