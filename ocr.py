import pytesseract
import easyocr
import cv2
from pprint import pprint
import shutil
import fitz
import numpy as np
import os
import re
import ftfy
from PIL import Image, ImageEnhance
from tqdm import tqdm

reader = easyocr.Reader(['en'])

# Paths to folders
PDF_IMAGES = "/Volumes/T7/PycharmProjects/OCR/PDF_Images"
PDF_PATH = "/Volumes/T7/PycharmProjects/OCR/PDFs"
IMG_PATH = "/Volumes/T7/PycharmProjects/OCR/Images"
RETRY_TO_PARSE_FAILED_IMGS = "/Volumes/T7/PycharmProjects/OCR/Retry"

# regex and config declaration
MYCONFIG = "--psm 11 --oem 3"
PAN_REGEX_2 = r"[A-Z]{6}[0-9]{3}[A-Z]{1}"
PAN_REGEX_1 = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
AADHAAR_REGEX = r"\b\d{4}\s?\d{4}\s?\d{4}\b"

# Flow: 1) Convert all the pdfs in PDF_Images folder to an image and store it 
#          in the PDF_Images Folder
#       2) Crop and Store all the Images in PDF_Images folder to The main 
#          Images folder.
#       3) Loop Through all the images in in the main Images folder and try
#          to extract Text from it
#       4) shift all the failed to extract text in the Retry folder and 
#          try again

def img_to_txt(img_path):
    image = Image.open(img_path)
    image = image.convert("L")
    # Convert PIL Image to NumPy array for OpenCV processing
    image_np = np.array(image)

    # Apply Median Blur to reduce noise
    image_np = cv2.medianBlur(image_np, 5)

    # Apply Adaptive Thresholding for better contrast
    image_np = cv2.adaptiveThreshold(image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    image = ImageEnhance.Contrast(image).enhance(0.6)
    extracted_text = pytesseract.image_to_string(image, config=MYCONFIG)
    extracted_text = extracted_text.replace("  ", " ").replace("\n", " ")
    fixed_text = ftfy.fix_text(extracted_text)
    return fixed_text

def extract_imgs_from_simple_pdfs():
    for pdf_name in os.listdir(PDF_PATH):
        if '.DS_Store' in PDF_PATH + "/" + pdf_name:
            continue
        doc = fitz.Document((os.path.join(PDF_PATH, pdf_name)))

        for i in tqdm(range(len(doc)), desc="pages"):
            for img in tqdm(doc.get_page_images(i), desc="page_images"):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                pix.save(os.path.join(PDF_IMAGES, "%s_p%s-%s.png" % (pdf_name[:-4], i, xref)))
        continue


def crop_n_store():
    for count, img in enumerate(os.listdir(PDF_IMAGES)):
        if '.DS_Store' in PDF_IMAGES + "/" + img:
            continue
        new_img = cv2.imread(PDF_IMAGES + "/" + img)
        gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to detect white ink and remove the background
        _,thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find external contours
        contours = cv2.findContours(morphed, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Process the top two largest contours (if available)
        for i, contour in enumerate(contours[:2]):  # Take the first two largest contours
            x, y, w, h = cv2.boundingRect(contour)
            crop = new_img[y:y+h, x:x+w]

            # Save each cropped image separately
            cropped_img_path = f'Images/{img}_contour{i}.png'
            cv2.imwrite(cropped_img_path, crop)
        os.remove("PDF_Images/" + img)
        
def Img_folder_loop(data_dict):
    for image in os.listdir(IMG_PATH):
        if '.DS_Store' in IMG_PATH + "/" + image:
            continue
        img_path = IMG_PATH + "/" + image
        extracted_text = img_to_txt(img_path)
        pan_match = re.search(PAN_REGEX_1, extracted_text)
        aadhar_match = re.search(AADHAAR_REGEX, extracted_text)
        if pan_match:
            pan_card_number = pan_match.group()
            data_dict[f"{image}"] = pan_card_number
        elif aadhar_match:
            aadhar_card_number = aadhar_match.group()
            data_dict[f"{image}"] = aadhar_card_number
        else:
            shutil.move(IMG_PATH + "/" + image, RETRY_TO_PARSE_FAILED_IMGS + "/" + image)
    return data_dict
            
def final_retry_pass(data_dict):
    for image in os.listdir(RETRY_TO_PARSE_FAILED_IMGS):
        if '.DS_Store' in RETRY_TO_PARSE_FAILED_IMGS + "/" + image:
            continue
        image_path = RETRY_TO_PARSE_FAILED_IMGS + "/" + image
        results_list = reader.readtext(image_path, detail=0)
        results_string = " ".join(results_list)
        pan_match_1 = re.search(PAN_REGEX_1, results_string)
        pan_match_2 = re.search(PAN_REGEX_2, results_string)
        aadhar_match = re.search(AADHAAR_REGEX, results_string)
        if pan_match_1:
            pan_card_number = pan_match_1.group()
            data_dict[f"{image}"] = results_list[7]
        elif pan_match_2:
            pan_number = results_list[7]
            corrected_pan = pan_number[:5] + pan_number[5:9].replace('O', '0') + pan_number[9:]
            data_dict[f"{image}"] = corrected_pan
        elif aadhar_match:
            aadhar_card_number = aadhar_match.group()
            data_dict[f"{image}"] = aadhar_card_number
    return data_dict

if __name__ == "__main__":
    data_dictionary = {}
    extract_imgs_from_simple_pdfs()
    crop_n_store()
    data_dict = Img_folder_loop(data_dictionary)
    final_data_dict = final_retry_pass(data_dict)
    print("Final Data Dictionary:\n")
    pprint(final_data_dict)