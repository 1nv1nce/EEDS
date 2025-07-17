import json
import openai
import time
import random
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
with open('dataset/relation_prompt.json', 'r', encoding='utf-8') as file:
    relation_prompt = json.load(file)

with open('processdata/train_seen.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

relation_learn = {
    "composer": [],
    "screenwriter": [],
    "languages spoken, written or signed": [],
    "sibling": [],
    "member of sports team": []
}

dicts = [{
    "composer": 0,
    "screenwriter": 0,
    "languages spoken, written or signed": 0,
    "sibling": 0,
    "member of sports team": 0,
    "__id__": i
} for i in range(len(data))]

for key in relation_prompt:
    for i in range(len(data)):
        for item in data[i]['labels']:
            if item['r'] in relation_prompt[key]:
                dicts[i][key] += 1

for key in relation_learn:
    sorted_dicts = sorted(dicts, key=lambda x: x[key], reverse=True)
    print("key: ", key)
    for i in range(100):
        temp = sorted_dicts[i][key]
        relation_learn[key].append(sorted_dicts[i]['__id__'])
        if(i == 99):
            print("temp: ", temp)
            print(sorted_dicts[i]['__id__'])
            print("-------------------")

with open('processdata/relation_learn.json', 'w', encoding='utf-8') as file:
    json.dump(relation_learn, file, ensure_ascii=False, indent=4)
        