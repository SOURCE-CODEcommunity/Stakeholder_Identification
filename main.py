from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import os
import re
import json
from datetime import datetime
from pydantic import BaseModel
from agent_ import run_agents


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file upload: {file.filename}")
    if not file.filename.endswith('.pdf'):
        logger.warning(f"Invalid file type: {file.filename}")
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})
    
    temp_pdf_file = f"temp_{file.filename}"
    with open(temp_pdf_file, "wb") as f:
        content = await file.read()
        f.write(content)

    with pdfplumber.open(temp_pdf_file) as pdf:
        text_content = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    

    cleaned_text = re.sub(r'\s+', ' ', text_content).strip()


    metadata = {
        "filename": file.filename,
        "uploadtime": datetime.utcnow().isoformat(),
        "wordcount": len(cleaned_text.split())
    }


    json_data = {
        "metadata": metadata,
        "cleaned_text": cleaned_text
    }

    try:
        stakeholder_details = await run_agents(cleaned_text)
        print("Generated Queries:", stakeholder_details)
        json_data["stakeholder_details"] = stakeholder_details
        json_data["stakeholder_details_length"] = len(stakeholder_details if not stakeholder_details is None else [])
    except Exception as e:
        print(e)

    # json_filename = f"extracted_data/{os.path.splitext(file.filename)[0]}_{int(datetime.utcnow().timestamp())}.json"
    # with open(json_filename, "w", encoding="utf-8") as json_file:
    #     json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    os.remove(temp_pdf_file)

    return {
        "status": "success",
        "filename": file.filename,
        "metadata": metadata,
        "preview": cleaned_text[:len(cleaned_text) if len(cleaned_text) < 500 else 500],
        "cleaned_text": cleaned_text,
        "stakeholder_details": stakeholder_details,
        "stakeholder_details_length": len(stakeholder_details if not stakeholder_details is None else [])
    }




# class QueryRequest(BaseModel):
#     project_text: str

# @app.post("/generate_queries")
# async def generate_queries(req: QueryRequest):
#     try:
#         queries = agent1_generate(req.project_text)
#         return {"queries": queries}
    
#     except Exception as e:

#         raise HTTPException(status_code=500, detail=str(e))
