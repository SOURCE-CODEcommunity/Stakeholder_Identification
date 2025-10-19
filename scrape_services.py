import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import pdfplumber
import io


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)
logger = logging.getLogger(__name__)


def convert_pdf_to_text(text: str) -> str:
    pdf_bytes = io.BytesIO(text)
    all_text = ""

    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + '\n'

    return all_text





def get_html_content(html: str) -> dict:



    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    cleaned_text = soup.get_text(separator=" ", strip=True)

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    email_from_text = re.findall(email_pattern, cleaned_text)

    email_from_tag = [a["href"].replace("mailto:", "") for a in soup.find_all("a", href=True) if "mailto:" in a["href"]]

    email_addresses = list(set(email_from_text + email_from_tag))


    social_domains = ["twitter.com", "linkedin.com", "facebook.com"]

    social_links = [a["href"] for a in soup.find_all("a", href=True) if any(domain in a["href"].lower() for domain in social_domains)]

    phone_pattern = r"(\+?\d{1,4}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,}[\s\-]?\d{2,})"

    phone_numbers = re.findall("phone_pattern", cleaned_text)

    phone_numbers_1 = list(set(phone_numbers))

    
    return {
        "cleaned_text": cleaned_text,
        "email_addresses": email_addresses,
        "social_links": social_links,
        "phone_numbers_1": phone_numbers_1
    }




def scrape_static(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            if ".pdf" in url.lower():
                cleaned_text = convert_pdf_to_text(response.content)
                logger.info(f"Pdf text: {cleaned_text}")
                return cleaned_text
            else:
                return response.text
                logger.info(f"Scraped static content from {url}: {response.text[:100]}...")
            
        elif response.status_code == 404:
            logger.warning(f"Page not found {url}: Status code {response.status_code}")
        else:
            logger.error(f"Failed to fetch {url}: Status code {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
    return ""


def scrape_dynamic(url: str) -> str:
    html = ""
    try:
        with sync_playwright() as p:
            browswer = p.chromium.launch(headless=True)
            page = browswer.new_page()
            if ".pdf" in url.lower():
                pdf_bytes = page.request.get(url).body()
                html = convert_pdf_to_text(pdf_bytes)
            else:
                page.goto(url, timeout=30000)
                page.wait_for_timeout(3000)
                html = page.content()

            browswer.close()
    except Exception as e:
        logger.error(f"Error scraping {url} dynamically: {str(e)}")

    logger.info(f"Scraped dynamic content from {url}: {html[:100]}...")
     
    return html


def scrape_urls(results: list) -> list:
    scrape_results = []
    for item in results:
        url = item["link"]
        html = scrape_static(url)
        html_content = get_html_content(html)

        if not html or len(html) < 500:
            html = scrape_dynamic(url)
            html_content = get_html_content(html)



        scrape_results.append({
            "title": item.get("title"),
            "link": url,
            "snippet": item.get("snippet"),
            "html_content": html_content,
        })

    logger.info(f"Scraped result check: {scrape_results}")

    return scrape_results



#if __name__ == "__main__":
    #import pdfplumber
    #test_url = "https://montefioreeinstein.org/documents/healingarts/song-Lyrics.pdf"
    # response = requests.get(test_url)
    # if response.status_code == 200:
    #     pdf_text = convert_pdf_to_text(response.content)
    #     logger.info(f"raw pdf {response.content}")
    #     logger.info(f"Extracted PDF Text: {pdf_text}")
    # else:
    #     logger.error(f"Failed to fetch PDF: Status code {response.status_code}")

    #html = scrape_static(test_url)
    #html = get_html_content(html)
    #logger.info(f"raw html {html}")
    