import json
from http_get_request import *
import os

with open('data/lemmaId_set.json', 'r') as f:
    lemmaId_set = set(json.load(f))

if os.path.exists('data/kexue/') == False:
    os.mkdir('data/kexue/')

for i in lemmaId_set:
    print(i)
    time.sleep(0.5)
    # https://baike.sogou.com/kexue/d69917841985450255.htm
    r = http_get_request(f'https://baike.sogou.com/kexue/d{i}.htm')
    with open(f'running.htm', 'w') as f:
        f.write(r.text)
    with open(f'data/kexue/d{i}.htm', 'w') as f:
        f.write(r.text)