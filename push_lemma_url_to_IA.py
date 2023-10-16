import json
import spn2api
spn2api.LOAD_API_AUTH('LOW ACC:SEC')

with open('data/lemmaId_set.json', 'r') as f:
    lemmaId_set = json.load(f)

count=0
for lemmaId in lemmaId_set:
    count+=1
    if count<= 180:
        continue
    print(count,'/',len(lemmaId_set),':',lemmaId)
    # https://baike.sogou.com/kexue/d69917841985450255.htm

    url = f'https://baike.sogou.com/kexue/d{lemmaId}.htm'
    spn2api.do_archive(url)