# Generate synthetic data for relation extraction task as output_data.json
import json
import openai
import time
import random
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

openai.api_key = "your openai key"
relation_prompt = 'dataset/relation_prompt.json'
# learn_data = 'processdata/learn_data.json'
results = []
rels = []

# open the learndata
try:
    with open('processdata/train_seen.json', 'r', encoding='utf-8') as file:
        learn_data = json.load(file)
except FileNotFoundError:
    print("Error: The file 'processdata/train_seen.json' was not found.")
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from the file.")

try:
    with open('processdata/relation_learn.json', 'r', encoding='utf-8') as file:
        learn_relation = json.load(file)
except FileNotFoundError:
    print("Error: The file 'processdata/relation_learn.json' was not found.")
except json.JSONDecodeError:
    print("Error: Failed to decode JSON from the file.")


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


def append_data_to_json(file_path, new_data):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    except json.JSONDecodeError:
        print("Failed to decode JSON, starting with an empty list")
        data = []
    data.append(new_data)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Data has been successfully appended to the file.")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")


def generate(relation_types):
    print("Start generating data......")
    print("----------------------------------------")
    # key_relation is the target unseen relation type, relationStr is the related relation types (include target relation type) selected by chatgpt
    for key_relation in relation_types:
        print("key: ",key_relation)
        relationStr="\", \"".join(relation_types[key_relation])
        # print(relationStr)
        # optional, you can change the content_theme to any themes
        content_theme="a famous individual, military force, melodious song, renowned club, political party, captivating book, opera, video game, film, TV serie, remarkable country, mesmerizing artwork, distinguished organization or influential company in the world"
        messages = []
        prompts = [
        f"""You are an information extraction assistant. To generate a high-quality paragraph for extracting relational triples, assume that three different experts are writing a fictional Wikipedia-style paragraph that contains at least 6 sentences and describes one or more of the following relationship types: "{relationStr}". The content of this generated fictional Wikipedia-style paragraph can be a description of {content_theme}. They write down their thoughts and then share them. Finally, The three experts debate and choose a high-quality paragraph that is most suitable for extracting relational triples. Simulate the process.""",
        f"""write the essay based on the remaining expert's ideas, with at least 6 sentences. Provide them in JSON format with just following keys: texts."""
        ]
        index = 0
        for pro in prompts:
            messages.append({'role': 'user', 'content': f"""{pro}"""})
            flag = 1
            thref = 0
            while flag:
                try:
                    if index == 0:
                        temperature = 1
                    else:
                        temperature = 0.0
                    response = get_completion_from_messages(messages, temperature=temperature)
                    # print(f"ChatGPT's synthetic response: {index}", response)
                except Exception as e:
                    print(e)
                    if thref >= 3:
                        break
                    print("wait 2 seconds!")
                    thref += 1
                    time.sleep(2)
                else:
                    flag = 0
            if flag == 1:
            # one of the prompts is not generated
                break
            messages.append({'role': 'assistant', 'content': f"""{response}"""})
            # print("messages: -------------------------------", messages)
            if index == 1:  
                print("success!")
                # print("ChatGPT's response to the second prompt:")
                results.append(response)
                rels.append(key_relation)  
            index += 1
        print("Finish the key_relation......")
    parsed_json_objects = []
    cnt = 0
    for result in results:
        try:
            result = result.replace("\n", "")
            result = result.replace("\"Hakuna Matata.\"", "\\\"Hakuna Matata\\\"")
            result = result.replace("Here is a fictional paragraph that describes the relation types \"place of birth\", \"place of death\", \"father\", \"mother\", and \"position held\":", "")
            result = result.replace("Here's an example paragraph:", "")
            result = result.replace("```{", "{")
            result = result.replace("]```", "]")
            result = result.replace("```This paragraph contains relations \"place of birth\" (Pella), \"father\" (King Philip II of Macedonia), \"mother\" (Queen Olympia), \"position held\" (King of Macedonia), \"place of death\" (Babylon).", "")
            result = result.replace("JSON Format:", "")
            result = result.replace("Relation Types:- Place of birth: \"Stagira, Greece\"- Father: \"Nicomachus\"- Mother: \"Phaestis\"- Place of death: \"Euboea, Greece\"- Position held: \"Philosopher and scientist\"", "")
            result = result.replace("As an information extraction assistant, I have generated a fictional paragraph with the following relation types: \"place of birth,\" \"place of death,\" \"father,\" \"mother,\" and \"position held.", "")
            result = result.replace("\"New Beginnings,\"", "\\\"New Beginnings\\\",")
            result = result.replace("\"In Memory Of,\"", "\\\"In Memory Of\\\",")
            result = result.replace("\"The Lost Souls\"", "\\\"The Lost Souls\\\"")
            result = result.replace("\"{  \"title\"", "{  \"title\"")
            result = result.replace("\"Shallow\"", "\\\"Shallow\\\"")
            result = result.replace("```json{", "{")
            result = result.replace("```json[", "[")
            result = result.replace("JSON format:{", "{")
            parsed_object = json.loads(result)
            # print("parsed_object: ", parsed_object)
            parsed_json_objects.append(parsed_object)
            parsed_object['relations'] = rels[cnt]
        except json.JSONDecodeError as e:
            print(f"Parsing error: {e} - When processing result: {result}")
        cnt += 1

    # Attempt to write the parsed objects to a JSON file
    try:
        with open('processdata/text.json', 'w', encoding='utf-8') as f:
            json.dump(parsed_json_objects, f, ensure_ascii=False, indent=4)
        print("JSON file has been successfully saved as 'text.json'.")
    except IOError as e:
        print(f"File writing error: {e}")
    # append_data_to_json('processdata/text.json', parsed_json_objects)

    print("Finish generating data......")
    print("----------------------------------------")


def learndata(relations):
    # print("Start learning data......")
    # print("----------------------------------------")
    random_value = random.choice(learn_relation[relations])
    # print(learn_relation[relations])
    # print(random_value)
    chosen = learn_data[random_value]
    prompt_text = f"###Document: {chosen['text']} ###Triplets: {json.dumps(chosen['labels'], ensure_ascii=False)}"
    # print(prompt_text)
    return prompt_text

def extraction():
    print("Start extracting data......")
    print("----------------------------------------")
    try:
        with open('processdata/text.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'processdata/text.json' was not found.")
        return
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
        return
    
    # Initialize the list to store merged data.

    # All relation types are listed in a string from ReDocRED
    all_relations = "head of government', 'country', 'place of birth', 'place of death', 'father', 'mother', 'spouse', 'country of citizenship', 'continent', 'instance of', 'head of state', 'capital', 'official language', 'position held', 'child', 'author', 'member of sports team', 'director', 'screenwriter', 'educated at', 'composer', 'member of political party', 'employer', 'founded by', 'league', 'publisher', 'owned by', 'located in the administrative territorial entity', 'operator', 'religion', 'contains administrative territorial entity', 'follows', 'followed by', 'headquarters location', 'cast member', 'producer', 'award received', 'creator', 'parent taxon', 'ethnic group', 'performer', 'manufacturer', 'developer', 'series', 'sister city', 'legislative body', 'basin country', 'located in or next to body of water', 'military branch', 'record label', 'production company', 'location', 'subclass of', 'subsidiary', 'part of', 'original language of work', 'platform', 'mouth of the watercourse', 'original network', 'member of', 'chairperson', 'country of origin', 'has part', 'residence', 'date of birth', 'date of death', 'inception', 'dissolved, abolished or demolished', 'publication date', 'start time', 'end time', 'point in time', 'conflict', 'characters', 'lyrics by', 'located on terrain feature', 'participant', 'influenced by', 'location of formation', 'parent organization', 'notable work', 'separated from', 'narrative location', 'work location', 'applies to jurisdiction', 'product or material produced', 'unemployment rate', 'territory claimed by', 'participant of', 'replaces', 'replaced by', 'capital of', 'languages spoken, written or signed', 'present in work', 'sibling'"
    all_relations = all_relations.replace("', '", "\", \" ")

    for cnt, entry in enumerate(tqdm(data, desc="Processing entries")):
        texts = entry.get('texts', [])
        relations = entry.get('relations', [])
        if isinstance(texts, list):
            texts = " ".join(texts)
        handle_text_extraction(texts, relations, all_relations)
    print("Finish extracting data......")
    print("----------------------------------------")

def handle_text_extraction(text, relations, all_relations):
    messages = []
    prompt_text = learndata(relations)
    # print("Prompt_text: ", prompt_text)
    prompts = [
        f"""{prompt_text}. ###Your goal is to learn the relational triplet extraction method for this example in preparation for the following work.""",
        f"""###Document: {text} ###Extract entities from the given document. Provide them in List of JSON format with the following keys: entity, entity type. The entity type can be one of the following types: "Organization", "Location", "Time", "Person", "Miscellaneous", "Number", "Blank". """,
        f"""Present the relational triplets as (h: head entity, t: tail entity, r: relation type), if a relationship exists between two entities. The relation type can be one or more of following relation types: "{all_relations}”. The entity type can be one or more from the previously extracted entity set. Organize the above triplet information in List of JSON format.""",
    ]
    index = 0
    for pro in prompts:
        messages.append({'role': 'user', 'content': pro})
        flag = 1
        thref = 0
        while flag:
            try:
                response = get_completion_from_messages(messages)
                # print(f"ChatGPT's extraction response: {index}", response)
                flag = 0
            except Exception as e:
                print(e)
                if thref >= 3:
                    print("Failed after several attempts, skipping this text.")
                    return  
                print("wait 2 seconds!")
                thref += 1
                time.sleep(2)
        messages.append({'role': 'assistant', 'content': response})
        # print("messages: -------------------------------", messages)
        # if index == 0:
        #     print("ChatGPT's response to the first prompt:")
        #     print(response)

        #修改index位置
        if index == 2: 
            try:
                response = response.replace("\n", "")
                response=response.replace("Here's the triplet information organized in List of JSON format, as per your request:```","")
                response = response.replace("```Note: The remaining seven triples cannot be supported or explained by the provided context or they might be incorrect interpretations.", "")
                response = response.replace("\": None","\": \" \" ")
                response = response.replace("Sure, here it is::", "")
                response = response.replace("Here is the information organized in a JSON format with the requested keys for each relational triplet:```", "")
                response = response.replace("]```", "]")
                response = response.replace("JSON Format:","")
                response = response.replace("```[", "[")
                response= response.replace("```For each triplet, the JSON object includes:- head entity: the main entity in the relationship- tail entity: the secondary entity in the relationship- relation type: the type of relationship between the entities- reasoning: an explanation of the significance of the relationship- context: the relevant sentence in which the relationship is mentioned in the original document.", "")
                response = response.replace("Sure, here is the information organized in a list of JSON format:```", "")
                response = response.replace("Sure, here it is:", "")
                response=response.replace("}}]","}]")
                response=response.replace("}}]For each triplet, the JSON object includes:- head entity: the main entity in the relationship- tail entity: the secondary entity in the relationship- relation type: the type of relationship between the entities- reasoning: an explanation of the significance of the relationship- context: the relevant sentence in which the relationship is mentioned in the original document.","}]")
                response=response.replace("Sure, here is the information organized in a list of JSON format:","")
                response=response.replace("Sure, here is the information organized in a list of JSON format with the requested keys:","")
                response=response.replace("Sure, here is the organized triplet information in List of JSON format:","")
                response=response.replace("This JSON format organizes the extracted relational triplets, along with their reasoning explanations and supporting sentences, in a structured and easy-to-read format.","")
                response=response.replace("Sure, here is the information organized in a list of JSON format with the requested keys:","")
                response=response.replace("I apologize for the confusion earlier, but I did not generate any relational triplets in the previous document. However, I can generate a list of JSON format for the entities extracted from the document with their corresponding support sentences. Here is the list:","")
                response=response.replace("I apologize for the confusion earlier. Here are the relational triplets based on the generated document, organized in a list of JSON format with the requested keys:","")
                response=response.replace("I apologize for the confusion earlier, as the document I generated did not contain any personal relationships or positions held by individuals. Therefore, I cannot provide reasoning explanations or supporting sentences for the extracted relational triplets.However, I can provide a general explanation of how the information can be organized in a list of JSON format. The list can contain one or more relational triplets, each represented as a JSON object with the following keys:- \"head entity\": the entity that appears as the subject of the relationship- \"tail entity\": the entity that appears as the object of the relationship- \"relation type\": the type of relationship between the head and tail entities- \"reasoning explanation\": a brief explanation of how the relationship was inferred from the text- \"supporting sentence\": the complete context of the sentence in the text that provides evidence for the relationshipHere is an example of how the information can be organized in a list of JSON format:","")
                response=response.replace("Sure, here is the organized information in List of JSON format:","")
                response=response.replace("Sure, here is the organized triplet information in a list of JSON format:","")
                response=response.replace("As mentioned earlier, I cannot generate relational triplets for the above document as it does not contain any information related to personal relationships or positions held by individuals. However, if there were such information, I could organize the triplet information in a list of JSON format with the following keys:","")
                response=response.replace("Note that this is just an example, and the actual JSON format may vary depending on the specific information and relationships extracted from the text.","")
                response=response.replace("Sure, here is the information organized in List of JSON format","")
                response=response.replace("I apologize for the confusion earlier. As mentioned earlier, there are no relational triplets in the generated document. However, I can provide a list of JSON format for each extracted entity in the document with the following keys:- Head entity- Tail entity- Relation type- Reasoning explanation of each relational triplet- Complete context of supporting sentence that shown in document","")
                response=response.replace("As there are no relational triplets in the generated document, I cannot provide the requested information. However, if there were relational triplets, the JSON format with the requested keys would look like this:","")
                response=response.replace("cinematic experience.\"}","cinematic experience.\"}]")
                response=response.replace("Since there were no relational triplets in the generated document, I will provide a list of JSON format for each extracted entity with the following keys: entity, entity type, and supporting sentence. Here is the list:","")
                response=response.replace("Sure, here is the list of JSON format with the requested keys:","")
                response=response.replace("As there are no relational triplets in the generated document, I cannot provide the requested information. However, I can provide a sample JSON format for a relational triplet:```","")
                response=response.replace("Sure, here's the information organized in a list of JSON format:","")
                response=response.replace("For each triplet, the JSON object includes:- head entity: the main entity in the relationship- tail entity: the secondary entity in the relationship- relation type: the type of relationship between the entities- reasoning: an explanation of the significance of the relationship- context: the relevant sentence in which the relationship is mentioned in the original document.","")
                response=response.replace("[    {","[{")
                response=response.replace("[  {","[{")
                response=response.replace("[ {","[{")
                response=response.replace("} ]","}]")
                response=response.replace("}  ]","}]")
                response=response.replace("}   ]","}]")
                response=response.replace("```json[","[")
                response=response.replace("```json","")
                print("\nsuccess!")
                # 找到第一个'['
                start_json_idx = response.find("[")
                # 找到第一个']'之后的位置
                end_json_idx = response.find("]", start_json_idx) + 1
                if end_json_idx == 0: 
                    if response[-1] != ']':
                        response += ']'
                    end_json_idx = len(response)
                json_str = response[start_json_idx:end_json_idx]
                triplets = json.loads(json_str)  
                # print("Triplets: \n", triplets)
                if(len(triplets) > 4):
                    new_data = {
                        'text': text,
                        'triples': triplets
                    }
                    append_data_to_json('processdata/merged_data_org1.json', new_data)
                    # print("Hello!!!")
                    # print("ChatGPT's response to the second prompt has been processed.")
            except json.JSONDecodeError as e:
                print(f"Parsing error: {e} - When processing result: {response}")
        index += 1

def main():
    n = 100
    relation_types = json.load(open(relation_prompt))
    for i in tqdm(range(n), desc="Generating data"):
        print("----------------------------------------")
        print(f"Generating data for the {i + 1}th time.")
        print("----------------------------------------")
        generate(relation_types) 
    extraction()
    with open('processdata/merged_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file) 
    print("length of synthetic data: ", len(data))
    with open('processdata/output_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)
    print("Finish all processes......")

if __name__ == "__main__":
    main()