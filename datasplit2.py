# change data to alpaca format and split data to unseen

import json

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def replace_ht_with_names(data):
    for entry in data:
        for label in entry['labels']:
            h_index = label['h']
            t_index = label['t']
            
            head_name = entry['vertexSet'][h_index][0]['name']
            tail_name = entry['vertexSet'][t_index][0]['name']
            
            label['h'] = head_name
            label['t'] = tail_name
    
    return data

def replace_relation_with_string(data, rel_info):
    for entry in data:
        for label in entry['labels']:
            index = label['r']
            relation = rel_info[str(index)]
            label['r'] = relation
    
    return data

def reorder_labels(data):
    for entry in data:
        for label in entry['labels']:
            ordered_label = {'h': label['h'], 't': label['t'], 'r': label['r']}
            label.clear()
            label.update(ordered_label)
    
    return data

def remove_elements(data):
    for entry in data:
        if 'title' in entry:
            del entry['title']
        if 'vertexSet' in entry:
            del entry['vertexSet']
    
    return data

def concatenate_sentences(data):
    for entry in data:
        concatenated_text = ' '.join([' '.join(sentence) for sentence in entry['sents']])
        entry['text'] = concatenated_text
        del entry['sents']  

    return data

def save_data_to_file(data, file_path):
    """将数据保存到JSON文件中。"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

# 加载数据
# file_path = 'dataset/train_revised.json'
file_path = 'dataset/dev.json'
data = load_json_file(file_path)

# 加载关系信息
rel_info_path = 'dataset/rel_info.json'
rel_info = load_json_file(rel_info_path)

# 替换数据中的索引为实体名
updated_data = replace_ht_with_names(data)

# 替换关系索引为关系字符串
updated_data = replace_relation_with_string(updated_data, rel_info)

# 重新排序labels
updated_data = reorder_labels(updated_data)

# 删除title和vertexSet
updated_data = remove_elements(updated_data)

# 合并句子
updated_data = concatenate_sentences(updated_data)

# 保存修改后的数据到新文件
# output_file_path = 'processdata/train_revised_seen.json'
output_file_path = 'dev_unseen.json'
save_data_to_file(updated_data, output_file_path)

with open(output_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

for e in data:
    unique_relations = list({label["r"] for label in e["labels"]})
    e["relations"] = unique_relations

# filtered_data = [e for e in data if len(e["labels"]) > 4]

# get the unseen relations
relations = ["composer", "screenwriter", "languages spoken, written or signed", "sibling", "member of sports team"]

final_data = []

for item in data:
    flag = 1
    for rel in item["labels"]:
        if rel["r"] in relations:
            flag = 0
            break
    if flag == 0:
        final_data.append(item)
    
save_data_to_file(final_data, output_file_path)
# save_data_to_file(filtered_data, output_file_path)

print(f"Data has been saved to {output_file_path}.")
