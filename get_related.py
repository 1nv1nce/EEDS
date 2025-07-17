#get the relation_prompt.json
import json
import openai
import time
import random
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

openai.api_key = "your openai key"

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]

all_relations = "head of government', 'country', 'place of birth', 'place of death', 'father', 'mother', 'spouse', 'country of citizenship', 'continent', 'instance of', 'head of state', 'capital', 'official language', 'position held', 'child', 'author', 'member of sports team', 'director', 'screenwriter', 'educated at', 'composer', 'member of political party', 'employer', 'founded by', 'league', 'publisher', 'owned by', 'located in the administrative territorial entity', 'operator', 'religion', 'contains administrative territorial entity', 'follows', 'followed by', 'headquarters location', 'cast member', 'producer', 'award received', 'creator', 'parent taxon', 'ethnic group', 'performer', 'manufacturer', 'developer', 'series', 'sister city', 'legislative body', 'basin country', 'located in or next to body of water', 'military branch', 'record label', 'production company', 'location', 'subclass of', 'subsidiary', 'part of', 'original language of work', 'platform', 'mouth of the watercourse', 'original network', 'member of', 'chairperson', 'country of origin', 'has part', 'residence', 'date of birth', 'date of death', 'inception', 'dissolved, abolished or demolished', 'publication date', 'start time', 'end time', 'point in time', 'conflict', 'characters', 'lyrics by', 'located on terrain feature', 'participant', 'influenced by', 'location of formation', 'parent organization', 'notable work', 'separated from', 'narrative location', 'work location', 'applies to jurisdiction', 'product or material produced', 'unemployment rate', 'territory claimed by', 'participant of', 'replaces', 'replaced by', 'capital of', 'languages spoken, written or signed', 'present in work', 'sibling'"
all_relations = all_relations.replace("', '", "\", \" ")
prompt = f"Select relation types that most related to the relation type \"composer\" from the following relation sets {all_relations} and give the reasons."
messages = []
messages.append({'role': 'user', 'content': f"""{prompt}"""})
print(get_completion_from_messages(messages))