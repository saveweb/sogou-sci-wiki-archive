from http_get_request import *
import json
import os

category_data_path='data/category'

# def path_build(level_path):
#     global category_data_path
#     path = os.getcwd()
#     path = os.path.join(path, category_data_path)
#     for i in level_path:
#         path = os.path.join(path, i)
#         if not os.path.exists(path):
#             os.mkdir(path)
#     return path

def write_json_file(json_data, path, filename):
    if not os.path.exists(path):
        os.mkdir(path)
    full_filename = os.path.join(path, filename)
    with open(full_filename, 'w') as f:
        f.write(json.dumps(json_data, indent=2, sort_keys=False, ensure_ascii=False))


catid=0
r=http_get_request(f'https://baike.sogou.com/kexue/data/category/tree?id={catid}')
json_data=r.json()

# print(json_data)

catid_set=set()
level_path=[]
lemmaId_set=set()

def get_all_catid(catid):
    global catid_set
    global level_path
    global lemmaId_set


    # time.sleep(3)
    # print('waiting 3 seconds')
    r=http_get_request(f'https://baike.sogou.com/kexue/data/category/tree?id={catid}')
    json_data=r.json()

    write_json_file(json_data, category_data_path, f'{catid}.json')# 保存json文件
    write_json_file(json_data, '.', f'running.json')# 保存json文件

    if 'data' in json_data:# 去掉 ['data'] 以外的
        json_data=json_data['data']

    if json_data['type']=='category':# 如果是分类
        id_=json_data['id']
        catid_set.add(id_)# id_ 是 str 类型
        level_path.append(id_)


    if json_data['edited'] :# 如果页面有实际内容
        lemmaId_set.add(json_data['lemmaId'])# 记录 lemmaId （str 类型）-> 页面的 id。
        print('id:', id_, '|', json_data['lemmaId'], '| category tree:', level_path,'...')
    else:
        print('id:', id_, '|', 'None', '| category tree:', level_path,'...')


    if json_data['type']=='category':
        for children_data in json_data['children']:
            if children_data['type']=='category':
                catid=children_data['id']
                if get_all_catid(catid) is True:
                    level_path.pop()
            if children_data['type']=='lemma' and children_data['edited']:
                lemmaId=children_data['id']
                print('id:', id_, '|', lemmaId, '| category tree:', level_path,'...')
                lemmaId_set.add(lemmaId)

    return True


# with open(f'data/category/{catid}.json', 'w') as f:
#     f.write(json.dumps(json_data, indent=2, sort_keys=False, ensure_ascii=False))
get_all_catid(0)


with open('data/lemmaId_set.json', 'w') as f:
    f.write(json.dumps(list(lemmaId_set), indent=2, sort_keys=False, ensure_ascii=False))

with open('data/catid_set.json', 'w') as f:
    f.write(json.dumps(list(catid_set), indent=2, sort_keys=False, ensure_ascii=False))

print(len(catid_set),len(lemmaId_set))
# print(lemmaId_set, len(lemmaId_set))