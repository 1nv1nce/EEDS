import json
import openai
import time
import random
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

openai.api_key = "your openai key"
relation_prompt = 'dataset/relation_prompt.json'
results = []

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]

import re
# 加载数据集和prompt
with open('processdata/testdata_dev.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
with open('prompts/prompt.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()
total_true_positive = 0
total_predicted = 0
total_actual = 0
idx = 0
# data=data[0:10]
def compare_triples(predicted_triples, true_triples):
    correct_count = 0
    try:
        true_triples_set = set(
            f"{triple['h']}|{triple['t']}|{triple['r']}" for triple in true_triples
        )
        for pred in predicted_triples:
            prediction_str = f"{pred['h']}|{pred['t']}|{pred['r']}"
            if prediction_str in true_triples_set:
                correct_count += 1
    except Exception as e:
        print(f"An error occurred while comparing triples: {e}")

    return correct_count
for item in tqdm(data, desc="Processing items"):
    text = item['text']
    true_triples = item['labels']
    # print(f"Item {idx + 1} of {len(data)}")
    idx += 1
    prompts = prompt + f"###input: {text}###output: "
    pro = [{'role': 'user', 'content': prompts}]
    try:
        predictions = get_completion_from_messages(pro)
    except:
        print("Failed to get completion from OpenAI API. Retrying...")
        time.sleep(5)
    prediction = predictions
    prediction = prediction.replace("\n", "")
    prediction = prediction.replace("Here's the triplet information organized in List of JSON format, as per your request:```","")
    prediction = prediction.replace("```Note: The remaining seven triples cannot be supported or explained by the provided context or they might be incorrect interpretations.", "")
    prediction = prediction.replace("\": None","\": \" \" ")
    prediction = prediction.replace("Sure, here it is::", "")
    prediction = prediction.replace("Here is the information organized in a JSON format with the requested keys for each relational triplet:```", "")
    prediction = prediction.replace("]```", "]")
    prediction = prediction.replace("JSON Format:","")
    prediction = prediction.replace("```[", "[")
    prediction = prediction.replace("```For each triplet, the JSON object includes:- head entity: the main entity in the relationship- tail entity: the secondary entity in the relationship- relation type: the type of relationship between the entities- reasoning: an explanation of the significance of the relationship- context: the relevant sentence in which the relationship is mentioned in the original document.", "")
    prediction = prediction.replace("Sure, here is the information organized in a list of JSON format:```", "")
    prediction = prediction.replace("Sure, here it is:", "")
    prediction = prediction.replace("Here is the information organized in a JSON format with the requested keys for each relational triplet:```", "")
    prediction = prediction.replace("]```", "]")
    prediction = prediction.replace("JSON Format:","")
    prediction = prediction.replace("```[", "[")
    prediction = prediction.replace("```json{","{")
    prediction = prediction.replace("```json","")
    prediction = prediction.replace("}}]","}]")
    prediction = prediction.replace("[    {","[{")
    prediction = prediction.replace("[  {","[{")
    prediction = prediction.replace("[ {","[{")
    prediction = prediction.replace("} ]","}]")
    prediction = prediction.replace("}  ]","}]")
    prediction = prediction.replace("}   ]","}]")
    prediction = prediction.replace("```json[","[")
    prediction = prediction.replace("```json","")
    # print("prediction: \n", prediction)
    # start_idx = prediction.find("###output:") + len("###output:")
    # # 找到第一个'['
    # start_json_idx = prediction.find("[", start_idx)
    # # 找到第一个']'之后的位置
    # end_json_idx = prediction.find("]", start_json_idx) + 1
    # if end_json_idx == 0: 
    #     if prediction[-1] != ']':
    #         if prediction[-1] == '}':
    #             prediction += ']'
    #         else:
    #             prediction += "}]"
    #     end_json_idx = len(prediction)
    # json_str = prediction[start_json_idx:end_json_idx]
    # json_str = json_str.replace("'", '"').replace('\\\\"', "\\'")
    # fixed_data = re.sub(r"(?<!\\)'(?=[^'\"]*?[\":])", '"', json_str)
    # print("json_str: \n", json_str)
    try:
        extracted_triples = json.loads(prediction)
        num_correct = compare_triples(extracted_triples, true_triples)
        total_true_positive += num_correct
        total_predicted += len(extracted_triples)
        total_actual += len(true_triples)
        print(f"Finish the {idx} item")
    except json.JSONDecodeError as e:
        # print("json_str: \n", fixed_data)
        print("Failed to decode JSON from the extracted string:", e)
    
    precision = total_true_positive / total_predicted if total_predicted > 0 else 0
    recall = total_true_positive / total_actual if total_actual > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"The {idx} score: Precision: {precision:.3f} Recall: {recall:.3f} F1 Score: {f1_score:.3f}")
print("Finish testing...")
print(f"The {idx} score: Precision: {precision:.3f} Recall: {recall:.3f} F1 Score: {f1_score:.3f}")