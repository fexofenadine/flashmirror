import glob
import os
import re
import requests
import shutil
import string
import sys
import urllib
from math import ceil
from pathlib import Path
from bs4 import BeautifulSoup

#script_name = sys.argv[0]
try:
    page_uri = sys.argv[1]
except:
    page_uri = ""

def mirror_flash(page_uri):
    soup = BeautifulSoup(urllib.request.urlopen(page_uri),features="html5lib")
    title=soup.title.string
    try:
        uploaded=soup.find("dt", string="Uploaded").find_next_sibling("dd").text
    except:
        uploaded="unknown"
    #strip branding and unfriendly characters
    title=title.replace("–","-").replace("™","").replace("Play ","").replace(", a free online game on Kongregate","").replace(" - Presented by Newgrounds!","").replace(" | Free Games Online at Armor Games","").replace(" | Strategy Games", "").replace(" - Kizi Games","").replace("Totaljerkface.com - Home Of Happy Wheels - ","").replace(" - on Crazy Games","").replace(" | Free Online Game","")
    #capitalize words regardless of punctuation
    title=re.sub(r"(?<=[a-z])[\']([A-Z])", lambda x: x.group().lower(), title.title())
    #fix remaining capitalization exceptions and consistent naming conventions
    title=title.replace(" Ii", " II").replace("Fpa:", "Fpa").replace("Fpa", "Fancy Pants Adventures").replace("The Fancy ", "Fancy ").replace(" - Super Smash Flash","").replace(" Eom", " EOM").replace(" Td ", " Tower Defense ").replace(" Ver", " ver").replace(" version", " Version").replace(" V2"," v2").replace("Rs ", "RS ")
    print("Title: "+title+" ("+uploaded+")")
    if uploaded == "unknown":
        suffix="_"
    else:
        suffix=""
    friendly_title=title.lower().translate(str.maketrans('', '', string.punctuation)).replace("–","-").replace(" ","_").replace("__","_")+suffix
    filename="flash/"+friendly_title+"/"+friendly_title

    soup = requests.get(page_uri)

    #print(str(soup.text))
    #swf_uri=re.findall(r'(http(s?)\:\/\/(.*)\.swf)', str(soup.text))[0][0]

    if "archive.org" in page_uri:
        print("Wayback Machine archive detected")
        try:
            uri=re.findall('embed src="/web/(................)_/(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]\.swf)', str(soup.content))[-1]
            swf_uri="https://web.archive.org/web/"+uri[0]+"/"+uri[1]+"://"+uri[2]+uri[3]
        except:
            uri=re.findall('(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]\.swf)', str(soup.content))[-1]
            swf_uri=uri[0]+"://"+uri[1]+uri[2]
    else:
        print("Assuming live website")
        uri=re.findall('(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]\.swf)', str(soup.content))[-1]
        swf_uri=uri[0]+"://"+uri[1]+uri[2]
    print (swf_uri)

    print("Generating html wrapper")
    output_html = None
    if Path('template.html').exists():
        with open('template.html') as f:
            template_html = f.read()
        output_html = template_html.replace('{swf_uri}', friendly_title+".swf")
        output_html = output_html.replace('{title}', title)
        output_html = output_html.replace('{uploaded}', uploaded)
        output_html = output_html.strip()
    output_file = Path("flash/"+friendly_title+"/index.html")
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file,'w') as f:
        f.write(output_html)

    #mirror flash file
    print("downloading "+uri[-1])
    response = requests.get(swf_uri, stream=True)
    if response.status_code == 200:
        with open(filename+".swf", 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

#build mirror file(s)
if page_uri:
    mirror_flash(page_uri)
else:
    with open("sources.txt","r") as f:
        for line in f:
            line=line.strip()
            if line != "" and line[0] != "#":
                print("Site: "+line)
                mirror_flash(line)

#build folder index
content_dir='./flash'
all_flash_wrappers=[]
flash_dirs=next(os.walk(content_dir))[1]
for flash_dir in list(flash_dirs):
    flash_wrappers=glob.glob(content_dir+'/'+flash_dir+'/*.html')
    all_flash_wrappers=all_flash_wrappers+flash_wrappers
output_string='<head>\n\t<meta name="robots" content="noindex">\n</head>\n<body style="background-color:222222; color:cobalt; font-weight: bold; font-size: large; font-family:monospace;">\n'
for flash_wrapper in list(all_flash_wrappers):
    soup = BeautifulSoup(open(flash_wrapper),features="html5lib")
    title=soup.title.string
    print("Flash wrapper: "+flash_wrapper+"\nTitle: "+title)
    flash_wrapper=flash_wrapper.replace("./flash",".")
    output_string=output_string+'\t<a href="'+flash_wrapper+'">'+title+'</a><br />\n'
output_string=output_string+'</body>'
with open("flash/index.html",'w') as f:
         f.write(output_string)