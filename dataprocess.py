#change output_data to alpaca format -> pre && posttransformdataset
import json

with open('prompt.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def update_key(data, old_key, new_key):
    if old_key in data:
        data[new_key] = data.pop(old_key)
    return data

def remove_keys(data, keys_to_remove):
    for key in keys_to_remove:
        data.pop(key, None)
    return data

def modify_labels(data):
    if 'output' in data:
        for label in data['output']:
            label = remove_keys(label, ['reasoning', 'evidence'])
    return data

def add_instructions(data):
    data['instruction'] = prompt
    return data

def reformat_data(item):
    text = f"{item['instruction']} ### input: {item['input']} ### output: {item['output']}"
    return {"text": text}

def transform_data(data):
    if isinstance(data, list):
        return [reformat_data(item) for item in data]
    else:
        return [reformat_data(data)]

file_path = 'processdata/output_data.json'
data = load_json_file(file_path)

keys_to_remove = ['title', 'vertexSet', 'relation_tag']
processed_data = []

if isinstance(data, list):
    for item in data:
        item = add_instructions(item)
        item = update_key(item, 'text', 'input')
        item = update_key(item, 'triples', 'output')
        # item = remove_keys(item, keys_to_remove)
        # item = modify_labels(item)
        processed_data.append(item)
    updated_data = processed_data
else:
    data = add_instructions(data)
    data = update_key(data, 'text', 'input')
    data = update_key(data, 'triples', 'output')
    # data = remove_keys(data, keys_to_remove)
    # data = modify_labels(data)
    updated_data = [data]
    
# Saving the untransformed data
pre_transform_path = 'processdata/PreTransformDataset.json'
save_json_file(updated_data, pre_transform_path)

# Transforming data
transformed_data = transform_data(updated_data)

# Saving the transformed data
post_transform_path = 'processdata/PostTransformDataset.json'
save_json_file(transformed_data, post_transform_path)

print("The JSON file has been processed. Data saved in two formats: 'PreTransformDataset.json' and 'PostTransformDataset.json'.")

