# import cv2
# import pytesseract
# from pytesseract import Output
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import numpy as np

# # Read image
# image = cv2.imread('input.jpg')

# # Convert to grayscale
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Apply thresholding
# threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# # OCR processing
# custom_config = r'--oem 3 --psm 6'
# details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')

# # Print the dictionary keys
# print(details.keys())

# # Convert BGR image to RGB (matplotlib uses RGB format)
# threshold_img_rgb = cv2.cvtColor(threshold_img, cv2.COLOR_BGR2RGB)

# # Create a figure and axis for matplotlib
# fig, ax = plt.subplots(1, figsize=(12, 8))

# # Display image
# ax.imshow(threshold_img_rgb)
# ax.set_title('Captured Text')
# ax.axis('off')  # Hide axes

# # Draw bounding boxes and labels
# total_boxes = len(details['text'])
# for sequence_number in range(total_boxes):
#     if int(details['conf'][sequence_number]) > 30:
#         (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number], details['height'][sequence_number])
#         # Draw a rectangle around the detected text
#         rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='green', facecolor='none')
#         ax.add_patch(rect)
#         # Annotate text on top of the rectangle
#         plt.text(x, y-10, details['text'][sequence_number], fontsize=8, color='red', ha='left', va='top')

# # Show the image with bounding boxes
# plt.show()

# # Arrange text into a format
# parse_text = []
# word_list = []
# last_word = ''

# for word in details['text']:
#     if word:
#         word_list.append(word)
#         last_word = word
#     if (last_word and not word) or (word == details['text'][-1]):
#         parse_text.append(word_list)
#         word_list = []

# # Save the text to a file
# import csv
# with open('result_text.txt', 'w', newline="") as file:
#     csv.writer(file, delimiter=" ").writerows(parse_text)



# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import pytesseract
# import numpy as np
# import cv2
# from PIL import Image
# import io
# import os

# app = FastAPI()

# # Initialize Jinja2 template engine
# templates = Jinja2Templates(directory="templates")

# # Serve static files (for images)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Define Tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return templates.TemplateResponse("upload_form.html", {"request": {}})

# @app.post("/upload/", response_class=HTMLResponse)
# async def upload_image(file: UploadFile = File(...)):
#     # Read image file
#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents))
    
#     # Convert image to OpenCV format
#     img = np.array(image)
    
#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
#     # Apply thresholding
#     threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
#     # OCR processing
#     custom_config = r'--oem 3 --psm 6'
#     details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT, config=custom_config, lang='eng')
    
#     # Draw bounding boxes and extract text
#     bounding_boxes = []
#     for i in range(len(details['text'])):
#         if int(details['conf'][i]) > 0:
#             (x, y, w, h) = (details['left'][i], details['top'][i], details['width'][i], details['height'][i])
#             bounding_boxes.append({"text": details['text'][i], "box": [x, y, x + w, y + h]})
#             cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
#     # Save processed image in the static directory
#     image_filename = "processed_image.png"
#     image_path = os.path.join("static", image_filename)
#     cv2.imwrite(image_path, threshold_img)
    
#     # Render the result HTML template with extracted text and image
#     return templates.TemplateResponse("result.html", {"request": {}, "image_filename": image_filename, "bounding_boxes": bounding_boxes})

# @app.get("/get_text/")
# async def get_text(x1: int, y1: int, x2: int, y2: int):
#     try:
#         # Load the image from the static directory
#         img_path = os.path.join("static", "processed_image.png")
#         img = cv2.imread(img_path)

#         if img is None:
#             raise ValueError("Image not found")

#         # Crop the image to the bounding box
#         cropped_img = img[y1:y2, x1:x2]

#         # OCR processing for the cropped image
#         custom_config = r'--oem 3 --psm 6'
#         text = pytesseract.image_to_string(cropped_img, config=custom_config, lang='eng')

#         return {"text": text.strip()}
#     except Exception as e:
#         return {"error": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import pytesseract
# import numpy as np
# import cv2
# from PIL import Image
# import io
# import os

# app = FastAPI()

# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return templates.TemplateResponse("index.html", {"request": {}})


# @app.post("/upload/", response_class=HTMLResponse)
# async def upload_image(file: UploadFile = File(...)):
#     allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

#     if file.content_type not in allowed_mimes:
#         raise HTTPException(status_code=400, detail="Unsupported file type")

#     try:
#         contents = await file.read()
#         image = Image.open(io.BytesIO(contents))    
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
#         for i in range(len(details['text'])):
#             if int(details['conf'][i]) > 0 and details['text'][i].strip():
#                 extracted_text.append(details['text'][i].strip())

#         # Save the uploaded image for display
#         image_filename = "uploaded_image.png"
#         image_path = os.path.join("static", image_filename)
#         image.save(image_path)

#         # Join all extracted text into a single string
#         extracted_text_str = " ".join(extracted_text)

#         # Return the template with the uploaded image and extracted text
#         return templates.TemplateResponse("index.html", {
#             "request": {},
#             "image_filename": image_filename,
#             "extracted_text": extracted_text_str
#         })

#     except Exception as e:
#         return HTMLResponse(content=f"An error occurred: {e}", status_code=500)
    
# @app.get("/get_text/")
# async def get_text(x1: int, y1: int, x2: int, y2: int):
#     try:
#         # Validate coordinates
#         if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
#             raise HTTPException(status_code=400, detail="Coordinates must be non-negative.")
        
#         # Load the image from the static directory
#         img_path = os.path.join("static", "processed_image.jpg")
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

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pytesseract
import numpy as np
import cv2
from PIL import Image
import io
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(file: UploadFile = File(...)):
    allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))    
        img = np.array(image)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Apply adaptive thresholding for better OCR results
        adaptive_threshold = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Perform OCR on the processed image
        custom_config = r'--oem 3 --psm 6'
        details = pytesseract.image_to_data(adaptive_threshold, output_type=pytesseract.Output.DICT, config=custom_config, lang='eng')

        # Extract text with bounding boxes
        extracted_text = []
        for i in range(len(details['text'])):
            if int(details['conf'][i]) > 0 and details['text'][i].strip():
                extracted_text.append(details['text'][i].strip())

        # Save the uploaded image for display
        image_filename = "uploaded_image.png"
        image_path = os.path.join("static", image_filename)
        image.save(image_path)

        # Join all extracted text into a single string
        extracted_text_str = " ".join(extracted_text)

        # Return the template with the uploaded image and extracted text
        return templates.TemplateResponse("index.html", {
            "request": {},
            "image_filename": image_filename,
            "extracted_text": extracted_text_str
        })

    except Exception as e:
        return HTMLResponse(content=f"An error occurred: {e}", status_code=500)

@app.get("/get_text/")
async def get_text(x1: int, y1: int, x2: int, y2: int):
    try:
        # Validate coordinates
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
            raise HTTPException(status_code=400, detail="Coordinates must be non-negative.")
        
        # Load the image from the static directory
        img_path = os.path.join("static", "uploaded_image.png")
        img = cv2.imread(img_path)

        if img is None:
            raise HTTPException(status_code=404, detail="Image not found")

        # Crop the image to the bounding box
        cropped_img = img[int(y1):int(y2), int(x1):int(x2)]

        # OCR processing for the cropped image
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(cropped_img, config=custom_config, lang='eng')

        return {"text": text.strip()}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)