from utils import get_system_message, use_chatgpt, search_wikipedia, search_sales_docs
import json

def brainstorm(user_query: str, notes: str, queries: str):

    system_message = get_system_message('system01_brainstorm_search_queries.txt')
    spr_system_message = get_system_message('system04_spr_refine.txt')
    user_message = (
f"""
# USER QUERY
{user_query}


# NOTES
{notes}


# PREVIOUS QUERIES
{queries}
"""
    )
    
    response, tokens = use_chatgpt(system_message, user_message)

    print(f"new questions = {response}")
    questions = json.loads(response)

    for question in questions:
        #content, url = search_wikipedia(question)
        content = search_sales_docs(question)
        compressed_content, spr_tokens = use_chatgpt(spr_system_message, content)
        tokens += spr_tokens

        #notes = f"{notes}\n\nURL: {source}\nNOTE: {compressed_content}"
        notes = f"{notes}\n\nNOTE: {compressed_content}"
        print(compressed_content)
        queries = (
f"""
{queries}

QUESTION: {question}

"""
        )
    
    return queries, notes, tokens
