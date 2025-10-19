from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import asyncio
from utils import clean_ai_json_response


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


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3,)


def chunk(text: str, max_chars: int = 8000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]


# def merge_all_chunked_response(responses: list) -> dict:
#     merge_data = {"stakeholders": [], "error": []}

#     for idx, resp in responses:
#         merge_data["stakeholders"].extend(resp["stakeholders"])

#     return merge_data



def merge_all_chunked_response(responses: list) -> dict:
    """
    Merge stakeholder data from multiple chunked responses.
    Each cleaned response is guaranteed to be a list of dicts.
    """
    merged = {"stakeholders": [], "error": []}

    for resp_list in responses:
        if not resp_list:
            merged["error"].append("Empty or invalid response chunk")
            continue

        for resp in resp_list:
            if isinstance(resp, dict) and "stakeholders" in resp:
                merged["stakeholders"].extend(resp.get("stakeholders", []))
            else:
                merged["error"].append(f"Unexpected response format: {resp}")

    return merged


async def extract_stakeholder(llm, chunk: str, idx: int, total: int):


    prompt = f"""
        You are an expert at extracting stakeholder information from websites.
        Extract the following from this chunk of text:
        - Names of stakeholders
        - Organization/Company
        - Emails
        - Phone numbers
        - Social media links (Twitter, LinkedIn, Facebook)
        - Any other relevant stakeholder data
        Format your answer as JSON.

        Here is an example of the JSON structure I expect:

        {{
            "stakeholders": [
                {{
                    "name": "Jane Doe",
                    "organization": "Acme Corp",
                    "email": "jane.doe@acmecorp.com",
                    "phone": "+1234567890",
                    "social_links": {{
                        "linkedin": "https://linkedin.com/in/janedoe",
                        "twitter": "https://twitter.com/janedoe",
                        "facebook": "https://facebook.com/janedoe"
                    }},
                    "other_info": "Interested in STEM educational projects"
                }}
            ]
        }}

        This is chunk {idx+1} of {total}.

        Text:
        {chunk}
        """

    response = await asyncio.to_thread(llm.invoke, prompt)
    return response.content.strip()


async def llm_call(results: list) -> list:
    logger.info("Got here!")
    try:
     
        async def process_text(result): 
            cleaned_text = result["html_content"]["cleaned_text"]
            pre_email_addresses = result["html_content"]["email_addresses"]
            pre_social_links = result["html_content"]["social_links"]
            pre_phone_numbers_1 = result["html_content"]["phone_numbers_1"]

            chunked_text = chunk(cleaned_text, max_chars=8000)

            chunked_response = await asyncio.gather(*[extract_stakeholder(llm, chunk, idx, len(chunk)) for idx, chunk in enumerate(chunked_text)])
            logger.info(f"Gemini Stakeholders Extract Not cleaned: {chunked_response}")
            clean_chunked_response = clean_ai_json_response(chunked_response)
            #gemini_data = merge_all_chunked_response(clean_chunked_response)
            logger.info(f"Gemini Stakeholders Extract Cleaned: {clean_chunked_response}")


            return {
                "title": result["title"],
                "link": result["link"],
                "snippet": result["snippet"],
                "emails": pre_email_addresses,
                "social_links": pre_social_links,
                "phone_links": pre_phone_numbers_1,
                "stakeholder_details": clean_chunked_response
            }

        return await asyncio.gather(*(process_text(result) for result in results))
    
    except Exception as e:
        logger.info(f"There was an error in llm_call. Check: {str(e)}")


# async def main():

#     results = [
#         {
#       "title": "AI to Make STEM Content for Neurodivergent Learners",
#       "link": "https://www.govtech.com/education/k-12/ai-to-make-stem-content-for-neurodivergent-learners",
#       "snippet": "Benetech, a nonprofit focused on equity in education, will launch an AI-powered system to make STEM learning materials accessible and interactive for students.",
#       "html_content": {
#         "cleaned_text": "AI to Make STEM Content for Neurodivergent Learners News Analytics Artificial Intelligence Civic Innovation Cloud & Computing Cybersecurity Lohrmann on Cybersecurity Education Election Technology Emerging Tech Budget & Finance Infrastructure Government Experience GovTech Biz Biz Data Health & Human Services Justice & Public Safety Broadband & Network Policy Smart Cities Transportation Workforce & People Voices Gov Efficiency Events Webinars Papers Magazine About About Us Advertise Newsletters Contact More Center for Digital Education Center for Digital Government Center for Public Sector AI Emergency Management Digital Communities Digital States GovTech Top 25 GovTech 100 Menu News Analytics Artificial Intelligence Civic Innovation Cloud & Computing Cybersecurity Lohrmann on Cybersecurity Education Election Technology Emerging Tech Budget & Finance Infrastructure Government Experience GovTech Biz Biz Data Health & Human Services Justice & Public Safety Broadband & Network Policy Smart Cities Transportation Workforce & People Voices Gov Efficiency Events Webinars Papers Magazine About About Us Advertise Newsletters Contact More Center for Digital Education Center for Digital Government Center for Public Sector AI Emergency Management Digital Communities Digital States GovTech Top 25 GovTech 100 Show Search CONTINUE TO SITE ✕ IE 11 Not Supported For optimal browsing, we recommend Chrome, Firefox or Safari browsers. Preparing K-12 and higher education IT leaders for the exponential era Home K-12 Higher Ed Events Webinars Newsletters Thought Leadership About Home K-12 Higher Ed Events Webinars Newsletters Thought Leadership About K-12 Education AI to Make STEM Content for Neurodivergent Learners Benetech, a nonprofit focused on equity in education, will launch an AI-powered system to make STEM learning materials accessible and interactive for students who are neurodivergent or visually impaired. January 28, 2025 • News Staff Facebook LinkedIn Twitter Print Email Shutterstock The education nonprofit Benetech is using artificial intelligence to convert science, technology, engineering and math (STEM) instructional materials into accessible content for students who are neurodivergent or visually impaired. As described in a news release this month, a new AI platform being developed by Benetech through student testing and pilot programs will be able to produce interactive content which those students can read, hear and also ask questions about. According to the National Center on Accessible Educational Materials , traditional reading materials can be a challenge for neurodivergent students to interact with, as they often involve complex text, equations and images that can be hard to read in a standard format or envision as presented via screen reader and basic alternative text. “Over 30 percent of neurodivergent or visually impaired students aspire to STEM careers, yet fewer than 10 percent achieve employment in STEM fields — a stark reminder of the persistent inaccessibility of STEM education,” Benetech CEO Ayan Kishore said in a public statement. “By harnessing the power of AI, we are transforming complex STEM materials into accessible formats, breaking down barriers, ensuring STEM education and careers are within reach for all.” Benetech’s mission is to create technology that can help deliver accessible educational materials to all learners, “while also changing the way content is created,” according to the nonprofit’s website . One of its services, Bookshare , is a free library of more than 1 million e-books that have been made accessible for people with disabilities. Others include accessibility training for teachers and a program that helps publishers make content accessible from the start. Funding for Benetech's new AI platform comes from General Motors, the Patrick J. McGovern Foundation, Cisco, the Esther and Pedro Rosenblatt Foundation, and the Peninsula Endowment, the news release said. Facebook LinkedIn Twitter Print Email Tags: K-12 Education Accessibility Artificial Intelligence STEM Digital Transformation News Staff See More Stories by News Staff Education Events Maryland Higher Education IT Leadership Summit June 5, 2025 Harvard IT Summit June 11, 2025 Ohio Higher Education IT Leadership Summit September 29, 2025 Massachusetts Higher Education IT Leadership Summit September 2025 Michigan Higher Education IT Leadership Summit September 2025 Georgia Higher Education IT Leadership Summit October 2025 New York/New Jersey Higher Education IT Leadership Summit October 2025 Arizona CIO/CTO Forum October 21, 2025 Texas Higher Education IT Leadership Summit November 20, 2025 Washington Higher Education IT Leadership Summit November 2025 CUNY IT Conference December 4-5, 2025 Maryland K-12 AI Leadership Conference December 2025 Related Content Higher Education University LLM Simulates Student Teaming on Math Problems September 26, 2025 · Abby Sourwine K-12 Education Sans Safeguards, AI in Education Risks Deepening Inequality September 26, 2025 · News Staff K-12 Education St. Petersburg, Fla., May Revive City’s Science Center September 26, 2025 K-12 Education Virginia School District Rolls Out New stem+M Program September 25, 2025 K-12 Education Pennsylvania Lawmaker Proposes AI Instructors Ban in Charters September 24, 2025 · Julia Gilban-Cohen K-12 Education School Districts Are Testing AI, but Few Have a Clear Strategy September 24, 2025 · News Staff Never miss a story with the GovTech Today newsletter. SUBSCRIBE twitter youtube facebook linkedin ©2025 All rights reserved. e.Republic LLC Do Not Sell My Personal Information | Privacy & AI",
#         "email_addresses": [
#           "?body=AI%20to%20Make%20STEM%20Content%20for%20Neurodivergent%20Learners%0A%0Ahttps%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners%0A%0ABenetech%2C%20a%20nonprofit%20focused%20on%20equity%20in%20education%2C%20will%20launch%20an%20AI-powered%20system%20to%20make%20STEM%20learning%20materials%20accessible%20and%20interactive%20for%20students%20who%20are%20neurodivergent%20or%20visually%20impaired."
#         ],
#         "social_links": [
#           "https://www.facebook.com/dialog/share?app_id=314190606794339&display=popup&href=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners",
#           "https://www.linkedin.com/shareArticle?url=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners&mini=true&title=AI%20to%20Make%20STEM%20Content%20for%20Neurodivergent%20Learners&summary=Benetech%2C%20a%20nonprofit%20focused%20on%20equity%20in%20education%2C%20will%20launch%20an%20AI-powered%20system%20to%20make%20STEM%20learning%20materials%20accessible%20and%20interactive%20for%20students%20who%20are%20neurodivergent%20or%20visually%20impaired.&source=GovTech",
#           "https://twitter.com/intent/tweet?url=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners&text=AI%20to%20Make%20STEM%20Content%20for%20Neurodivergent%20Learners",
#           "https://www.facebook.com/dialog/share?app_id=314190606794339&display=popup&href=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners",
#           "https://www.linkedin.com/shareArticle?url=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners&mini=true&title=AI%20to%20Make%20STEM%20Content%20for%20Neurodivergent%20Learners&summary=Benetech%2C%20a%20nonprofit%20focused%20on%20equity%20in%20education%2C%20will%20launch%20an%20AI-powered%20system%20to%20make%20STEM%20learning%20materials%20accessible%20and%20interactive%20for%20students%20who%20are%20neurodivergent%20or%20visually%20impaired.&source=GovTech",
#           "https://twitter.com/intent/tweet?url=https%3A%2F%2Fwww.govtech.com%2Feducation%2Fk-12%2Fai-to-make-stem-content-for-neurodivergent-learners&text=AI%20to%20Make%20STEM%20Content%20for%20Neurodivergent%20Learners",
#           "https://twitter.com/govtechnews",
#           "https://www.facebook.com/governmenttechnology",
#           "https://www.linkedin.com/company/government-technology/"
#         ],
#         "phone_numbers_1": []
#       }
#     }
#     ]
#     await llm_call(results)


# if __name__ == "__main__":
    

#      asyncio.run(main())