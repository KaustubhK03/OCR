# 🧾 OCR-Based Document Identifier Extractor

This project is an Automated Document Analyzer that processes PDF and image files to extract PAN and Aadhaar card numbers using pytesseract and easyocr. It involves multiple stages: converting PDFs to images, cropping relevant sections, text extraction, and re-processing failed cases.

## 📁 Folder Structure

project-root/
│
├── PDFs/               # Input PDFs
├── PDF_Images/         # Images extracted from PDFs
├── Images/             # Cropped images for OCR
├── Retry/              # Images for retrying OCR
├── main.py             # Main pipeline script

---

## 🚀 Features

- ✅ Extracts text from both **images and PDFs**
- 🔍 Detects **PAN** and **Aadhaar** numbers using **regex**
- 🧹 Uses **grayscale**, **blur**, and **adaptive thresholding** for image preprocessing
- 🔁 **Retry mechanism** using `easyocr` for failed OCR attempts
- 📊 Outputs a structured **dictionary** mapping filenames to extracted IDs

---

## 🛠️ Technologies Used

- `pytesseract` – Python wrapper for Tesseract OCR
- `easyocr` – Deep learning-based OCR
- `opencv-python` – Image processing
- `fitz` (`PyMuPDF`) – PDF parsing and image extraction
- `ftfy` – Fixes text encoding issues
- `Pillow` – Image enhancement
- `tqdm` – CLI progress bars

---

## 📦 Installation

Make sure Python **3.8+** is installed.

```bash
# Clone this repository
git clone https://github.com/KaustubhK03/OCR.git
cd OCR

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

Required packages (requirements.txt):
pytesseract
easyocr
opencv-python
PyMuPDF
Pillow
ftfy
tqdm

Also, install Tesseract OCR engine:
	•	Mac: brew install tesseract
	•	Ubuntu: sudo apt install tesseract-ocr
	•	Windows: Download Installer

 How to Run

Ensure the following folders exist and contain the appropriate files:
	•	Place input PDFs in PDFs/ folder.

Then run:
python main.py

Output will be a printed dictionary mapping filenames to extracted PAN/Aadhaar numbers.

Processing Flow
	1.	Extract Images from PDF: Each page image is extracted and saved to PDF_Images/.
	2.	Crop Images: Top 2 largest white ink contours are cropped and saved in Images/.
	3.	Initial OCR Pass: Tries extracting PAN/Aadhaar numbers from Images/ using Tesseract.
	4.	Retry Pass: If Tesseract fails, image is moved to Retry/ and processed with EasyOCR.
	5.	Output: Final dictionary contains image names and their corresponding IDs.

 Sample Output
 {
  "aadhaar_1.png": "1234 5678 9123",
  "pan_5.png": "ABCDE1234F"
}

Notes
	•	.DS_Store files (macOS) are ignored.
	•	Includes two regex patterns for PAN to improve matching accuracy.
	•	Failed OCR retries use a correction mechanism to fix common OCR errors (e.g., ‘O’ vs ‘0’).


Author

Kaustubh Kalambkar
Feel free to reach out for contributions, feedback, or improvements!
