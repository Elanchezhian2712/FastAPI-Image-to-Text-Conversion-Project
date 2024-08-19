# from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, Form
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import pytesseract
# import numpy as np
# import cv2
# from PIL import Image
# import io
# import os
# from datetime import datetime
# from sqlalchemy.orm import Session

# from src.crud import create_candidate_data
# from src.database import SessionLocal  
# from src.models import CandidateData 

# # Database dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # FastAPI application instance
# app = FastAPI()

# # Template and static files setup
# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Tesseract command path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Root endpoint
# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return templates.TemplateResponse("index.html", {"request": {}})

# # Image upload and OCR processing
# @app.post("/upload/", response_class=HTMLResponse)
# async def upload_image(file: UploadFile = File(...)):
#     allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

#     if file.content_type not in allowed_mimes:
#         raise HTTPException(status_code=400, detail="Unsupported file type")

#     try:
#         contents = await file.read()
#         image = Image.open(io.BytesIO(contents))

#         # Convert to RGB if the image is grayscale
#         if image.mode != "RGB":
#             image = image.convert("RGB")

#         img = np.array(image)

#         # Convert the image to grayscale
#         gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

#         # Apply adaptive thresholding for better OCR results
#         adaptive_threshold = cv2.adaptiveThreshold(
#             gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
#         )

#         # Perform OCR on the processed image
#         custom_config = r'--oem 3 --psm 6'
#         details = pytesseract.image_to_data(adaptive_threshold, output_type=pytesseract.Output.DICT, config=custom_config, lang='eng')

#         # Extract text with bounding boxes
#         extracted_text = []
#         boxes = []
#         for i in range(len(details['text'])):
#             if int(details['conf'][i]) > 0 and details['text'][i].strip():
#                 text = details['text'][i].strip()
#                 extracted_text.append(text)
#                 (x, y, w, h) = (details['left'][i], details['top'][i], details['width'][i], details['height'][i])
#                 boxes.append((x, y, x + w, y + h, text))

#         # Save the uploaded image for display
#         image_filename = "uploaded_image.png"
#         image_path = os.path.join("static", image_filename)
#         image.save(image_path)

#         # Render the result page with the extracted text and bounding boxes
#         return templates.TemplateResponse("index.html", {
#             "request": {},
#             "image_filename": image_filename,
#             "boxes": boxes
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# # Get text from cropped image
# @app.get("/get_text/")
# async def get_text(x1: int, y1: int, x2: int, y2: int):
#     try:
#         # Validate coordinates
#         if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
#             raise HTTPException(status_code=400, detail="Coordinates must be non-negative.")
        
#         # Load the image from the static directory
#         img_path = os.path.join("static", "uploaded_image.png")
#         img = cv2.imread(img_path)

#         if img is None:
#             raise HTTPException(status_code=404, detail="Image not found")

#         # Crop the image to the bounding box
#         cropped_img = img[int(y1):int(y2), int(x1):int(x2)]

#         # OCR processing for the cropped image
#         custom_config = r'--oem 3 --psm 6'
#         text = pytesseract.image_to_string(cropped_img, config=custom_config, lang='eng')

#         return {"text": text.strip()}
#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         return {"error": str(e)}

# # Submit candidate data to the database
# @app.post("/submit_data/")
# def submit_data(
#     govt_rank: str = Form(...),
#     application_number: str = Form(...),
#     name: str = Form(...),
#     dob: str = Form(...),
#     aggregate_mark: str = Form(...),
#     community: str = Form(...),
#     govt_community_rank: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         dob_date = datetime.strptime(dob, "%Y-%m-%d").date()

#         # Call the CRUD function to create the new data
#         create_candidate_data(db, govt_rank, application_number, name, dob_date, aggregate_mark, community, govt_community_rank)

#         return {"message": "Data submitted successfully!"}
#     except Exception as e:
#         return {"error": str(e)}

from fastapi import Depends, FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2
from PIL import Image
import io
import os
from datetime import datetime
from sqlalchemy.orm import Session
import re
import warnings
from paddleocr import PaddleOCR

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from src.crud import create_candidate_data
from src.database import SessionLocal
from src.models import CandidateData

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI application instance
app = FastAPI()

# Template and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize PaddleOCR with table recognition enabled
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

# Image upload and OCR processing using PaddleOCR
@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(file: UploadFile = File(...)):
    allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        if image.mode != "RGB":
            image = image.convert("RGB")

        img = np.array(image)
        result = ocr.ocr(img, cls=True)

        if not result:
            raise HTTPException(status_code=404, detail="No text found in the image.")

        extracted_text = []
        boxes = []
        for line in result:
            for word_info in line:
                text = word_info[1][0]
                bbox = word_info[0]
                confidence = word_info[1][1]

                if confidence > 0.5 and text.strip():
                    extracted_text.append(text.strip())
                    x, y, w, h = int(bbox[0][0]), int(bbox[0][1]), int(bbox[2][0] - bbox[0][0]), int(bbox[2][1] - bbox[0][1])
                    boxes.append((x, y, x + w, y + h, text))

        image_filename = "uploaded_image.png"
        image_path = os.path.join("static", image_filename)
        image.save(image_path)

        # Convert extracted text to structured format (example)
        # You may need to adjust this based on the table structure
        structured_data = []
        for box in boxes:
            x1, y1, x2, y2, text = box
            structured_data.append({
                "text": text,
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })

        return templates.TemplateResponse("index.html", {
            "request": {},
            "image_filename": image_filename,
            "boxes": boxes,
            "extracted_text": extracted_text,
            "structured_data": structured_data
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/get_text/")
async def get_text(x1: int = Query(...), y1: int = Query(...), x2: int = Query(...), y2: int = Query(...)):
    try:
        # Validate coordinates
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            raise HTTPException(status_code=400, detail="Coordinates must be non-negative.")

        # Load the image from the static directory
        img_path = os.path.join("static", "uploaded_image.png")
        img = cv2.imread(img_path)

        if img is None:
            raise HTTPException(status_code=404, detail="Image not found")

        # Validate coordinates against image dimensions
        if x1 >= img.shape[1] or y1 >= img.shape[0] or x2 > img.shape[1] or y2 > img.shape[0]:
            raise HTTPException(status_code=400, detail="Coordinates out of bounds")

        # Crop the image to the selected region
        cropped_img = img[y1:y2, x1:x2]

        # Save the cropped image for debugging (optional)
        cv2.imwrite("static/cropped_image.png", cropped_img)

        # Perform OCR on the cropped image
        result = ocr.ocr(cropped_img, cls=True)

        if not result:
            raise HTTPException(status_code=400, detail="No text detected")

        # Extract the text from the result
        extracted_text = ' '.join([word_info[1][0] for line in result for word_info in line])

        return {"text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Submit candidate data to the database
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

        # Call the CRUD function to create the new data
        create_candidate_data(db, govt_rank, application_number, name, dob_date, aggregate_mark, community, govt_community_rank)

        return {"message": "Data submitted successfully!"}
    except Exception as e:
        return {"error": str(e)}

def extract_field(text, field_name):
    # Define a pattern to find the field and its value
    pattern = re.compile(rf'{field_name}:\s*(\S+)')
    match = pattern.search(text)
    if match:
        return match.group(1)
    return None
