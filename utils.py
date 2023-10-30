import requests
import time
import os
import sys
import random
from termcolor import colored
import pathlib
import openai
from halo import Halo
import time
import settings
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector
from azure.core.credentials import AzureKeyCredential


def chatbot(conversation, model=settings.OPENAI_MODEL, temperature=0, max_tokens=2000):
    max_retry = 7
    retry = 0
    openai.api_key = settings.OPENAI_API_KEY
    openai.api_base = settings.OPENAI_API_BASE
    openai.api_type = settings.OPENAI_API_TYPE
    openai.api_version = settings.OPENAI_API_VERSION

    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            
            response = openai.ChatCompletion.create(engine=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            retry += 1
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            time.sleep(5)
            if retry >= max_retry:
                exit()


# Define the function to use the ChatGPT API
def use_chatgpt(system_message, user_message):
    conversation = list()
    conversation.append({'role': 'system', 'content': system_message})
    conversation.append({'role': 'user', 'content': user_message})
    response, tokens = chatbot(conversation)
    return response, tokens

def search_wikipedia(query: str) -> (str, str):

    spinner = Halo(text='Information Foraging...', spinner='dots')
    spinner.start()

    url = 'https://en.wikipedia.org/w/api.php'
    search_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': query,
        'format': 'json'
    }

    response = requests.get(url, params=search_params)
    data = response.json()

    title = data['query']['search'][0]['title']

    content_params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'titles': title,
        'format': 'json'
    }

    response = requests.get(url, params=content_params)
    data = response.json()

    page_id = list(data['query']['pages'].keys())[0]

    content = data['query']['pages'][page_id]['extract']

    url = f"https://en.wikipedia.org/?curid={page_id}"

    spinner.stop()

    return content, url

def search_sales_docs(query: str) -> (str, str):

    spinner = Halo(text='Information Foraging...', spinner='dots')
    spinner.start()

    index_name: str = "sales_vector_index"
    credential_search = AzureKeyCredential(settings.AZURE_SEARCH_ADMIN_KEY)

    search_client = SearchClient(
                endpoint=settings.AZURE_SEARCH_ENDPOINT,
                index_name=index_name,
                credential=credential_search,
            )
    
    vector = Vector(value=get_embedding(query, settings.OPENAI_MODEL_EMBED), k=3, fields="summaryVector, contentVector")
    results = []

    r = search_client.search(  
            search_text=query,  # set this to engage a Hybrid Search
            vectors=[vector],  
            select=["sourcefile", "content"],
            top=3,
        )  
    for doc in r:
        results.append(f"[SOURCEFILE:  {doc['sourcefile']}]\n" + doc['content'])
        #print("\n".join(results))

    spinner.stop()
    
    return ("\n".join(results))

def get_system_message(file_name: str):

    # assume the prompts arev all in a directory called prompts at the root of where main.py is running
    prompts_root = pathlib.Path(__file__).parent
    prompts_dir = "prompts"
    prompt_file_path = prompts_root / prompts_dir / file_name
 
    #print(prompt_file_path)

    # Check if the file exists before trying to read it
    if prompt_file_path.exists() and prompt_file_path.is_file():
        # Open and read the file
        with open(prompt_file_path, 'r') as f:
            content = f.read()
        return content
    else:
        raise ValueError(f"The file {prompt_file_path} does not exist.")

def get_embedding(text, model):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], engine=model)['data'][0]['embedding']
