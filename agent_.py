import os
import json
import re
import asyncio
from typing import TypedDict, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from search_services import search_all
from scrape_services import scrape_urls
from llm_module import llm_call

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)
logger = logging.getLogger(__name__)

load_dotenv()

def clean_with_regex(raw_string):
    """
    Use regex to extract quoted strings from the malformed data
    """
    # Find all quoted strings
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, raw_string)
    
    # Filter out non-content matches (like 'json', etc.)
    content_items = []
    for match in matches:
        # Skip short items that are likely formatting artifacts
        if len(match) > 10 and not match in ['json']:
            content_items.append(match)
    
    return content_items


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3,)

class AgentState(TypedDict):

    project_text: str
    queries: List[str]
    search_results: List[dict]
    scrape_results: List[dict]
    stakeholder_details: List[dict]


def generate_queries_node(state: AgentState) -> AgentState:

    project_text = state["project_text"]

    prompt = f"""
                You are an expert research assistant.
                Given the following project description, generate 1 *specific* search queries
                that could be used to find stakeholders (people, organizations, agencies, NGOs, companies)
                interested in this project.

                Project description:
                {project_text}

                Return ONLY a valid JSON list of strings like:
                ["query 1", "query 2", ...]
                """

    response = llm.invoke(prompt)

    content = response.content.strip()

    try:
        query_list = json.loads(content)

    except json.JSONDecodeError:
        #query_list = [line.strip('-•') for line in content.split('\n') if line.strip()]
        cleaned_list_2 = clean_with_regex(content)
        query_list = cleaned_list_2 if cleaned_list_2 else ["No valid queries generated"]

    return {"queries": query_list}



def search_node(state: AgentState) -> AgentState:
    queries = state["queries"]
    
    all_results = []

    for query in queries:
        results = search_all(query, num_results=1)
        all_results.append({
            "query": query,
            "results": results
        })

    return {"search_results": all_results}


def scrape_node(state: AgentState) -> AgentState:
    search_results = state["search_results"]

    results = [
        {
            "query": item["query"],
            "title": result["title"],
            "link": result["link"],
            "snippet": result["snippet"]
        }
        for item in search_results
        for result in item["results"]
        
    ]
    scrape_result = scrape_urls(results)

    logger.info(f"Scraping completed with {len(scrape_result)} results.")
    logger.info(f"Scraping completed: {scrape_result}")

    return {"scrape_results": scrape_result}


async def stakeholder_details_node(state: AgentState) -> AgentState:
    scrape_data = state["scrape_results"]
    stakeholder_details = await llm_call(scrape_data)
    logger.info(f"Final Stakeholder Details: {stakeholder_details}")
    all_stakeholders_details = [stakeholder for page in stakeholder_details for stakeholder in page.get("stakeholder_details", {}).get("stakeholders", [])]
    logger.info(f"Last Final Stakeholder Details: {all_stakeholders_details}")
    return {"stakeholder_details": stakeholder_details}

builder = StateGraph(AgentState)

builder.add_node("generate_queries", generate_queries_node)
builder.add_node("search", search_node)
builder.add_node("scrape_urls", scrape_node)
builder.add_node("generate_stakeholder_details", stakeholder_details_node)

builder.set_entry_point("generate_queries")

builder.add_edge("generate_queries", "search")
builder.add_edge("search", "scrape_urls")
builder.add_edge("scrape_urls", "generate_stakeholder_details")


builder.set_finish_point("generate_stakeholder_details")

graph = builder.compile()


async def run_agents(project_text: str):
    result = {}
    try:
        result = await graph.ainvoke({"project_text": project_text})

    except Exception as e:
        print(f"Error: {str(e)}")

    return result.get("stakeholder_details")
