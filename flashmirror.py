import re
import shutil
import sys
from math import ceil
from pathlib import Path
import requests

script_name = sys.argv[0]
swf_uri = sys.argv[1]

print (swf_uri)
html_response = requests.get(swf_uri).content
print(html_response)