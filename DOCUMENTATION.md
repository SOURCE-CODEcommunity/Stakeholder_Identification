# Stakeholders Identification System Backend Documentation

## Overview

This backend system is designed to automate the identification and extraction of stakeholders from uploaded PDF documents and web resources. It leverages AI (Google Gemini via LangChain), web scraping, and search APIs to find, extract, and structure stakeholder information such as names, organizations, emails, phone numbers, and social media links.

---

## Features

- **PDF Upload & Text Extraction**: Accepts PDF files, extracts and cleans text.
- **Automated Query Generation**: Uses AI to generate search queries based on project descriptions.
- **Web Search Integration**: Aggregates results from Google Custom Search and SerpAPI.
- **Web Scraping**: Scrapes static and dynamic web pages for relevant content.
- **Stakeholder Extraction**: Uses LLM to extract structured stakeholder data from text.
- **Data Storage**: Saves extracted data and metadata as JSON files.
- **Logging**: All operations are logged for traceability.

---

## Main Components

### 1. `main.py`

- **Framework**: FastAPI
- **Endpoints**:
  - `POST /upload`: Accepts PDF uploads, extracts text, runs the stakeholder identification pipeline, and returns a preview and metadata.
- **Logging**: All uploads and errors are logged to `app.log`.
- **Data Output**: Results are saved in the `extracted_data/` directory as JSON files.

### 2. `agent_.py`

- **Purpose**: Orchestrates the multi-step agent workflow using LangGraph.
- **Pipeline Steps**:
  1. **Query Generation**: AI generates search queries from project text.
  2. **Search**: Aggregates search results from Google and SerpAPI.
  3. **Scraping**: Scrapes URLs for content.
  4. **Stakeholder Extraction**: AI extracts stakeholder details from scraped content.
- **Async Execution**: Supports async invocation for scalability.

### 3. `llm_module.py`

- **LLM Integration**: Uses Google Gemini via LangChain for all AI tasks.
- **Chunking**: Splits large texts for processing.
- **Response Merging**: Merges and cleans chunked AI responses.
- **Stakeholder Extraction**: Prompts LLM to extract structured stakeholder data.

### 4. `search_services.py`

- **Search APIs**: Integrates Google Custom Search and SerpAPI.
- **Aggregation**: Combines results from multiple sources.
- **Error Handling**: Logs and handles API errors gracefully.

### 5. `scrape_services.py`

- **Static & Dynamic Scraping**: Uses `requests` for static and Playwright for dynamic content.
- **PDF Handling**: Extracts text from PDFs found online.
- **Content Cleaning**: Extracts emails, phones, and social links from HTML.

### 6. `utils.py`

- **Cleaning Functions**: Regex-based cleaning and AI response parsing.
- **Error Logging**: Handles and logs JSON decode errors.

---

## Data Flow

1. **User uploads PDF** →
2. **Text extracted and cleaned** →
3. **AI generates search queries** →
4. **Search APIs return relevant links** →
5. **Web scraping extracts page content** →
6. **LLM extracts stakeholder info** →
7. **Results saved as JSON**

---

## File Structure

- `backend/`
  - `main.py` — FastAPI app and entry point
  - `agent_.py` — Agent workflow orchestration
  - `llm_module.py` — LLM integration and utilities
  - `search_services.py` — Search API integration
  - `scrape_services.py` — Web scraping utilities
  - `utils.py` — Helper functions
  - `extracted_data/` — Output JSON files
  - `app.log` — Log file
  - `requirements.txt` — Python dependencies

---

## Setup & Usage

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**: (Google API keys, SerpAPI, etc.)
3. **Run the server**: `uvicorn main:app --reload`
4. **Upload PDF via `/upload` endpoint**
5. **Check `extracted_data/` for results**

---

## Environment Variables

- `GOOGLE_SEARCH_API_KEY` — Google Custom Search API key
- `GOOGLE_CX` — Google Custom Search Engine ID
- `SERP_API_KEY` — SerpAPI key
- (Other keys as required by `.env`)

---

## Logging

- All logs are written to `app.log` in the backend directory.

---

## Dependencies

- FastAPI
- pdfplumber
- requests
- playwright
- beautifulsoup4
- langchain-google-genai
- python-dotenv
- (See `requirements.txt` for full list)

---

## Authors & Contact

- System designed and implemented by your team.
- For support, check logs or contact the maintainer.

---

## License

- [Specify your license here]

---

## Final Output Structure

The final output for each processed PDF is saved as a JSON file in the `extracted_data/` directory. The structure is as follows:

```json

{
  "metadata": {
    "filename": "AI-Powered Lecture Video Generator (1).pdf",
    "uploadtime": "2025-09-28T23:50:57.146500",
    "wordcount": 6604
  },
  "cleaned_text": "AI-Powered Lecture Video Generator project using Python & OpenGL. Includes AI Prompt Interpreter, Scene Model, OpenGL Renderer, Animation Engine, and Video Exporter ...",
  "stakeholder_details": [
    {
      "title": "QuestionWell…",
      "link": "https://questionwell.org/",
      "snippet": "Discover the best…",
      "emails": [ ],
      "social_links": [
         "https://www.linkedin.com/company/teachfloor/",
     "https://twitter.com/teachfloor"
],
      "Phone_links": [ ],
      "stakeholder_details": {
        "stakeholders": [
          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },

          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },

          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },
          //... more stakeholders

        ]
      }
    },
    {
      "title": "QuestionWell…",
      "link": "https://questionwell.org/",
      "snippet": "Discover the best…",
      "emails": [ ],
      "social_links": [
         "https://www.linkedin.com/company/teachfloor/",
     "https://twitter.com/teachfloor"
],
      "Phone_links": [ ],
      "stakeholder_details": {
        "stakeholders": [
          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },

          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },

          { "name": string, "organization": string, "email": string, "phone": string, "social_links":{"linkedin": string, "twitter": string, "facebook": string},
"other_info": string },
          //... more stakeholders

        ]
      }
    },
    //... more upper level in the list
  ],
  "stakeholder_details_length": 2
}
```
- Each JSON file contains the original filename, upload time, word count, the cleaned text, and a list of extracted stakeholders with their details.
- Errors encountered during extraction are included in the `error` array.
- The `stakeholder_details_length` field gives a quick count of stakeholders found.

---