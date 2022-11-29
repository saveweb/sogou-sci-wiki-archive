import json
from spn2api import *
from parsel import Selector
LOAD_API_AUTH('LOW $accesskey:$secret')

with open('data/lemmaId_set.json', 'r', encoding='utf8') as f:
    lemmaId_set = json.load(f)

count=0
markdown=''
for lemmaId in lemmaId_set:
    count+=1
    print(count,'/',len(lemmaId_set),':',lemmaId)
    # https://baike.sogou.com/kexue/d69917841985450255.htm

    with open(f'data/kexue/d{lemmaId}.htm', 'r', encoding='utf8') as f:
        html=f.read()
        selector = Selector(text=html)
        h1=selector.css('h1::text').get()

    url = f'https://baike.sogou.com/kexue/d{lemmaId}.htm'
    r=http_get_request(f'https://archive.org/wayback/available?url={url}')
    data=r.json()

    if 'closest' not in data['archived_snapshots']:
        markdown+=f'- [{h1}](https://web.archive.org/web/20220000000000*/{url}) (非直链)\n'
        continue

    if data["archived_snapshots"]["closest"]["available"]:
        print(f'[{h1}]({data["archived_snapshots"]["closest"]["url"]})')
        markdown+=f'- [{h1}]({data["archived_snapshots"]["closest"]["url"]})\n'
    else:
        print("erro")
        break

with open('archived_page.md','w',encoding='utf8') as f:
    f.write(markdown)