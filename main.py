# import pytesseract
# from PIL import Image
# import pandas as pd
# import re

# # Path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Load the image
# image_path = 'input.jpg'
# img = Image.open(image_path)

# # Extract bounding boxes for each word
# detection_boxes = pytesseract.image_to_boxes(img)
# print("Bounding boxes extracted from the image:")
# print(detection_boxes)

# # Extract the text
# raw_text = pytesseract.image_to_string(img)

# # Function to clean and process text
# def clean_text(raw_text):
#     cleaned_text = re.sub(r'[_|]', '', raw_text)  # Remove unwanted characters
#     cleaned_text = cleaned_text.replace('— ', '')  # Remove long dashes
#     return cleaned_text

# # Clean the extracted text
# cleaned_text = clean_text(raw_text)

# # Process the cleaned text
# def extract_text_from_boxes(boxes_text):
#     lines = boxes_text.split('\n')
#     data = []
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue

#         # Example regex pattern to match expected format
#         pattern = re.compile(r'^(\d+)\s+(\d+)\s+(.+?)\s+(\d{2}-\d{2}-\d{4})\s+([\d\.]+)\s+(\w+)\s+(\d+)$')
#         match = pattern.match(line)
#         if match:
#             try:
#                 rank = match.group(1).strip()
#                 application_number = match.group(2).strip()
#                 name = match.group(3).strip()
#                 dob = match.group(4).strip()
#                 aggregate_mark = match.group(5).strip()
#                 community = match.group(6).strip()
#                 community_rank = match.group(7).strip()
#                 data.append([rank, application_number, name, dob, aggregate_mark, community, community_rank])
#             except Exception as e:
#                 print(f"Error processing line: {line}\nError: {e}")
#     return data

# # Process the text with bounding boxes
# data = extract_text_from_boxes(cleaned_text)

# # Define columns for DataFrame
# columns = ['GOVT RANK', 'APPLICATION NUMBER', 'NAME OF THE CANDIDATE', 'DATE OF BIRTH', 'AGGREGATE MARK', 'COMMUNITY', 'GOVT COMMUNITY RANK']

# # Convert the data to a DataFrame
# df = pd.DataFrame(data, columns=columns)

# # Save the DataFrame to an Excel file
# output_path = 'extracted_data1.xlsx'
# df.to_excel(output_path, index=False)

# print(f"Data extracted and saved to {output_path}")

from fastapi import FastAPI, Depends, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import pytesseract
import pandas as pd
import os
import base64
import re
from datetime import datetime
from database import SessionLocal
from models import CandidateData
import pytesseract

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define Pydantic model for incoming data
class CandidateDataCreate(BaseModel):
    govt_rank: str
    application_number: str
    name: str
    dob: str
    aggregate_mark: str
    community: str
    govt_community_rank: str

    class Config:
        orm_mode = True

# Serve static files (index.html)
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    file_path = "templates/index.html"
    if os.path.exists(file_path):
        with open(file_path) as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="Index file not found", status_code=404)


# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read image asynchronously
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))
        
        # Extract text using pytesseract
        raw_text = pytesseract.image_to_string(image)
        
        # Process the text to extract data
        data = process_text(raw_text)
        
        # Convert the data to DataFrame
        df = pd.DataFrame(data, columns=['GOVT RANK', 'APPLICATION NUMBER', 'NAME OF THE CANDIDATE', 'DATE OF BIRTH', 'AGGREGATE MARK', 'COMMUNITY', 'GOVT COMMUNITY RANK'])
        
        # Create a BytesIO object and save the DataFrame to it
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        output.seek(0)
        
        # Convert BytesIO to a base64 encoded string
        binary_string = base64.b64encode(output.getvalue()).decode('utf-8')
        return JSONResponse(content={"excel_data": binary_string})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
    
def process_text(text: str) -> list:
    lines = text.split('\n')
    data = []
    pattern = re.compile(r'^(\d+)\s+(\d+)\s+(.+?)\s+(\d{2}-\d{2}-\d{4})\s+([\d\.]+)\s+(\w+)\s+(\d+)$')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            try:
                rank = match.group(1).strip()
                application_number = match.group(2).strip()
                name = match.group(3).strip().replace('_|', '').replace('—', '')  # Clean up names
                dob_str = match.group(4).strip()
                aggregate_mark = match.group(5).strip()
                community = match.group(6).strip()
                community_rank = match.group(7).strip()

                # Convert the date of birth string to a datetime.date object
                dob = datetime.strptime(dob_str, '%d-%m-%Y').date()
                
                data.append([rank, application_number, name, dob, aggregate_mark, community, community_rank])
            except Exception as e:
                print(f"Error processing line: {line}\nError: {e}")
    return data

@app.post("/submit_data/")
def submit_data(
    govt_rank: str = Form(...),
    application_number: str = Form(...),
    name: str = Form(...),
    dob: str = Form(...),
    aggregate_mark: str = Form(...),
    community: str = Form(...),
    govt_community_rank: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()

        new_data = CandidateData(
            govt_rank=govt_rank,
            application_number=application_number,
            name=name,
            dob=dob_date,
            aggregate_mark=aggregate_mark,
            community=community,
            govt_community_rank=govt_community_rank
        )

        # Add and commit the new record synchronously
        db.add(new_data)
        db.commit()  # Synchronous commit
        return {"message": "Data submitted successfully!"}
    except Exception as e:
        db.rollback()  # Synchronous rollback
        return {"error": str(e)}
