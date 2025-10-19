import os
import json
import re
import requests

from dotenv import load_dotenv

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

def search_google(query: str, num_results: int = 5):
    """
    Search using Google Custom Search API.
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "q": query,
        "key": api_key,   # correct parameter name for API key
        "cx": cx,
        "num": num_results
    }

    logger.info(f"Google Search params: {params}")

    try:
        response = requests.get(url, params=params)
    except requests.RequestException as e:
        logger.error(f"Error during Google Search API request: {str(e)}")
        return []

    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })

        logger.info(f"Google returned {len(results)} results for '{query}'")
        return results
    else:
        logger.error(f"Google API error: {response.status_code} - {response.text}")
        return []


def search_serp(query: str, num_results: int = 5):
    """
    Search using SerpAPI.
    """
    api_key = os.getenv("SERP_API_KEY")
    url = "https://serpapi.com/search"

    params = {
        "q": query,
        "api_key": api_key,
        "num": num_results
    }

    logger.info(f"SerpAPI params: {params}")

    try:
        response = requests.get(url, params=params)
    except requests.RequestException as e:
        logger.error(f"Error during SerpAPI request: {str(e)}")
        return []

    if response.status_code == 200:
        data = response.json()
        # SerpAPI doesn't always have 'items'; often 'organic_results'
        items = data.get("items") or data.get("organic_results", [])
        results = []
        for item in items:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })

        logger.info(f"SerpAPI returned {len(results)} results for '{query}'")
        return results
    else:
        logger.error(f"SerpAPI API error: {response.status_code} - {response.text}")
        return []


def search_all(query: str, num_results: int = 5):
    """
    Aggregate results from all APIs.
    """
    all_results = []

    logger.info(f"Starting combined search for '{query}'")

    res1 = search_google(query, num_results)
    all_results.extend(res1)

    res2 = search_serp(query, num_results)
    all_results.extend(res2)

    logger.info(f"Total combined results: {len(all_results)}")

    return all_results
