# FastAPI Image-to-Text Conversion Project

Welcome to the FastAPI Image-to-Text Conversion Project! This repository provides a FastAPI-based application designed to convert images into text using Optical Character Recognition (OCR). Users can upload images, extract text, and submit the extracted data to a database through a user-friendly web interface.

# Project Overview

This project leverages FastAPI for backend development, with a combination of HTML, CSS, and JavaScript for the frontend. The core functionality involves:

Image Upload: Users can upload images via a web interface.
Text Extraction: The application processes the images to extract text using OCR.
Interactive Text Editing: Users can drag and select text areas within the uploaded image.
Data Submission: Extracted text is associated with input labels and submitted to a database.


## Project Structure
```
demo/
│
├── main.py # Main FastAPI application entry point
├── src/ # Source code directory
│ ├── crud.py # CRUD operations
│ ├── database.py # Database configurations
│ └── models.py # Database models
├── run.bat # Batch script to run the application
└── env/ # Virtual environment directory
```

## Setup Instructions

Follow these steps to set up and run the project:

1. **Create and activate the virtual environment:**

   ```sh
   .\env\Scripts\activate

pip install -r req.txt


##Run the application:
run.bat


# Features
   1. Image Upload: Easily upload images through the web interface.
   2. OCR Text Extraction: Automatically convert images to text using OCR technology.
   3. Interactive Text Editing: Drag and select text from the image for precise extraction.
   4. Data Submission: Submit extracted text to a database with associated input labels.
   5. Database Integration: Uses Subase for managing and storing extracted text data.

# Technologies Used
   1. FastAPI: High-performance web framework for building APIs.
   2. OCR: Optical Character Recognition for text extraction.
   3. HTML/CSS/JavaScript: Frontend technologies for creating the web interface.
   4. Subase: Database management system for storing extracted data.

