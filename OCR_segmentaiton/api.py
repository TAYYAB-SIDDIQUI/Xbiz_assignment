import os
import pytesseract
import cv2
from paddleocr import PaddleOCR
from flask import Flask,request,render_template,jsonify
import json

app=Flask(__name__)

json_file = 'data.json'
if not os.path.isfile(json_file):
    with open(json_file, 'w') as f:
        json.dump([], f)


def text_extraction(path):
    img = cv2.imread(path)
    blur = cv2.GaussianBlur(img, (5,5), 2)
    sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)

    # Grayscale and background normalization
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    norm = cv2.divide(gray, bg, scale=255)
    cv2.imwrite("processed_images/image.png",norm)
    ocr= PaddleOCR(use_angle_cls=True,lang="en")
    text=ocr.ocr("processed_images/image.png")
    list_text=text
    return list_text

import cv2
import numpy as np
# def group_text_blocks(texts, boxes, vertical_threshold=15):
#     grouped_texts = []
#     grouped_boxes = []

#     for i, (text, box) in enumerate(zip(texts, boxes)):
#         x_coords = [point[0] for point in box]
#         y_coords = [point[1] for point in box]
#         mid_y = (min(y_coords) + max(y_coords)) / 2
        
#         added = False
#         for idx, group_box in enumerate(grouped_boxes):
#             group_ys = [point[1] for point in group_box]
#             group_mid_y = (min(group_ys) + max(group_ys)) / 2
            
#             if abs(mid_y - group_mid_y) < vertical_threshold:
#                 # Add text
#                 grouped_texts[idx] += " " + text
                
#                 # Merge boxes by combining all points from both boxes
#                 grouped_boxes[idx] = grouped_boxes[idx] + box
#                 added = True
#                 break

#         if not added:
#             grouped_texts.append(text)
#             grouped_boxes.append(box)

#     # Optionally, reduce each group_box points to a minimal bounding rectangle
#     final_boxes = []
#     for group_box in grouped_boxes:
#         xs = [p[0] for p in group_box]
#         ys = [p[1] for p in group_box]
#         min_x, max_x = min(xs), max(xs)
#         min_y, max_y = min(ys), max(ys)
#         # Bounding rectangle corners in order (top-left, top-right, bottom-right, bottom-left)
#         rect = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
#         final_boxes.append(rect)

#     return grouped_texts, final_boxes

# def annotate_extracted_fields(image_path, paddle_ocr_result, extracted_fields, save_path="annotated.png"):
#     image = cv2.imread(image_path)

#     # Flatten PaddleOCR result: [(box, (text, conf))]
#     texts =paddle_ocr_result[0]["rec_texts"]
#     boxes = paddle_ocr_result[0]["rec_boxes"]
#     text_blocks, block_boxes = group_text_blocks(texts, boxes)

#     print(text_blocks)  # List of grouped text strings (lines)
#     print(block_boxes)  # Corresponding bounding boxes for each grouped line


#     # Define color codes
#     colors = {
#         "aadhaar_number": (0, 255, 0),
#         "dob": (255, 0, 0),
#         "gender": (0, 0, 255),
#         "issuer": (255, 255, 0),
#         "name": (255, 0, 255)
#     }

#     for points, text in boxes:
#         label = None
#         text_lower = text.lower()
#         # Match extracted fields
#         for key, value in extracted_fields.items():
#             if value and isinstance(value, str) and value.lower() in text_lower:
#                 label = key
#                 break
#         if label:
#             color = colors.get(label, (0, 255, 255))
#             cv2.polylines(image, [points], isClosed=True, color=color, thickness=2)
#             # Label text
#             x, y = points[0]
#             cv2.putText(image, label.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     cv2.imwrite(save_path, image)
#     print(f"Annotated image saved as: {save_path}")

def detect_document_type(text_blocks):
    print(text_blocks)
    text = ' '.join(text_blocks).lower()
    print(text)

    if 'uidai' in text or 'aadhaar' in text or re.search(r'\d{4}\s\d{4}\s\d{4}', text):
        return 'aadhaar'
    elif 'income tax' in text or 'permanent account number' in text or re.search(r'[A-Z]{5}\d{4}[A-Z]', text):
        return 'pan'
    elif 'driving licence' in text or 'rto' in text or 'valid till' in text or re.search(r'[A-Z]{2}[- ]?\d{2,4}[- ]?\d{7,}', text):
        return 'dl'
    elif 'election commission' in text or 'voter id' in text or 'epic' in text:
        return 'voter'
    elif 'account number' in text or 'ifsc' in text or 'transaction' in text or 'debit' in text or 'credit' in text:
        return 'bank'
    else:
        return 'unknown'

import re
import difflib

def extract_adhaar_text(text_blocks):
    fields = {
        'aadhaar_number': None,
        'dob': None,
        'gender': None,
        'issuer': None,
        'raw_blocks': text_blocks,
        'is_valid_aadhaar': False
    }

    for block in text_blocks:
        block_lower = block.lower()

        # Detect issuer - fuzzy match for UIDAI or "govt"
        if any(word in block_lower for word in ['uidai', 'gov', 'india']):
            fields['issuer'] = 'UIDAI'

        # Detect gender
        if 'male' in block_lower:
            fields['gender'] = 'MALE'
        elif 'female' in block_lower:
            fields['gender'] = 'FEMALE'

        # Detect date of birth
        dob_match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', block)
        if dob_match:
            fields['dob'] = dob_match.group()

        # Detect Aadhaar number
        aadhaar_match = re.search(r'\d{4}\s\d{4}\s\d{4}', block)
        if aadhaar_match:
            fields['aadhaar_number'] = aadhaar_match.group()

        # Handle slight OCR errors in Aadhaar
        fallback_match = re.search(r'(\d[\s\d]{13,17})', block)
        if fallback_match and not fields['aadhaar_number']:
            digits = re.sub(r'\D', '', fallback_match.group())
            if len(digits) == 12:
                fields['aadhaar_number'] = f"{digits[:4]} {digits[4:8]} {digits[8:]}"
    
    # Final validity check
    fields['is_valid_aadhaar'] = fields['aadhaar_number'] is not None and fields['issuer'] is not None
    return fields
    
def extract_pan_fields(ocr_blocks):
    fields = {
        'pan_number': None,
        'name': None,
        'father_name': None,
        'dob': None,
        'is_valid_pan': False
    }

    for block in ocr_blocks:
        text = block.strip()
        
        # PAN Number: e.g., ABCDE1234F
        pan_match = re.search(r'[A-Z]{5}\d{4}[A-Z]', text)
        if pan_match:
            fields['pan_number'] = pan_match.group()

        # DOB
        dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        if dob_match:
            fields['dob'] = dob_match.group()

        # Fuzzy matching for Father and Name
        if "father" in text.lower():
            fields['father_name'] = text
        elif "name" in text.lower() and not fields['name']:
            fields['name'] = text

    fields['is_valid_pan'] = fields['pan_number'] is not None
    return fields


def extract_voter_fields(ocr_blocks):
    fields = {
        'voter_id': None,
        'name': None,
        'gender': None,
        'dob': None,
        'is_valid_voter': False
    }

    for block in ocr_blocks:
        text = block.strip()

        voter_match = re.search(r'[A-Z]{3}[0-9]{7}', text)
        if voter_match:
            fields['voter_id'] = voter_match.group()

        if 'female' in text.lower():
            fields['gender'] = 'FEMALE'
        elif 'male' in text.lower():
            fields['gender'] = 'MALE'

        if re.search(r'\d{2}/\d{2}/\d{4}', text):
            fields['dob'] = re.search(r'\d{2}/\d{2}/\d{4}', text).group()

        if "name" in text.lower():
            fields['name'] = text

    fields['is_valid_voter'] = fields['voter_id'] is not None
    return fields

def extract_dl_fields(ocr_blocks):
    fields = {
        'dl_number': None,
        'name': None,
        'dob': None,
        'valid_till': None,
        'is_valid_dl': False
    }

    for block in ocr_blocks:
        text = block.strip()

        # DL Format (e.g. DL-0420110149646)
        dl_match = re.search(r'[A-Z]{2}[- ]?\d{2,4}[- ]?\d{7,}', text)
        if dl_match:
            fields['dl_number'] = dl_match.group().replace(" ", "").replace("-", "")

        if re.search(r'\d{2}/\d{2}/\d{4}', text):
            date = re.search(r'\d{2}/\d{2}/\d{4}', text).group()
            if not fields['dob']:
                fields['dob'] = date
            else:
                fields['valid_till'] = date

        if "name" in text.lower():
            fields['name'] = text

    fields['is_valid_dl'] = fields['dl_number'] is not None
    return fields

def extract_bank_fields(ocr_blocks):
    fields = {
        'account_number': None,
        'ifsc_code': None,
        'transactions': [],
        'balance': None,
        'is_valid_statement': False
    }

    for block in ocr_blocks:
        text = block.strip()

        # Account number pattern
        acc_match = re.search(r'X{2,}\d{3,5}', text)
        if acc_match:
            fields['account_number'] = acc_match.group()

        # IFSC
        ifsc_match = re.search(r'[A-Z]{4}0[A-Z0-9]{6}', text)
        if ifsc_match:
            fields['ifsc_code'] = ifsc_match.group()

        # Transaction pattern
        txn_match = re.findall(r'\d{2}/\d{2}/\d{4}.*?[-+]?\d{1,3}(,\d{3})*(\.\d{2})?', text)
        if txn_match:
            fields['transactions'].append(text)

        # Balance line
        if 'balance' in text.lower() and re.search(r'\d{1,3}(,\d{3})*(\.\d{2})?', text):
            balance = re.search(r'\d{1,3}(,\d{3})*(\.\d{2})?', text).group()
            fields['balance'] = balance

    fields['is_valid_statement'] = fields['account_number'] is not None or len(fields['transactions']) > 0
    return fields

documents=os.listdir("docs")
print(documents)

def data(path):

    text_input=text_extraction(path)
    document_type=detect_document_type(text_input[0]["rec_texts"])
    print(text_input[0]["rec_boxes"],len(text_input[0]["rec_boxes"][0]))
    print(document_type)
    if document_type=="aadhaar":
        aadhaar_data=extract_adhaar_text(text_input[0]["rec_texts"])
        #annotate_extracted_fields("processed_images/image.png", text_input, aadhaar_data, save_path="annotated_aadhaar.png")
        response={"document_type":document_type,"aadhaar_data":aadhaar_data}
    elif document_type=="pan":
        pan_data=extract_pan_fields(text_input[0]["rec_texts"])
        response={"document_type":document_type,"pan_data":pan_data}
    elif document_type=="dl":
        dl_data=extract_dl_fields(text_input[0]["rec_texts"])
        response={"document_type":document_type,"driving license":dl_data}
    elif document_type=="voter":
        voter_data=extract_voter_fields(text_input[0]["rec_texts"])
        response={"document_type":document_type,"voter_data":voter_data}
    elif document_type=="bank":
        bank_data=extract_bank_fields(text_input[0]["rec_texts"])
        response={"document_type":document_type,"bank_data":bank_data}
    else:
        response={"document_type":"other","data":text_input[0]["rec_texts"]}
    with open(json_file, 'r') as f:
        data = json.load(f)
    data.append(response)

    # Save updated list back to file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    return response

# for i in os.listdir("docs"):
#     print(data(f"docs/{i}"))

@app.route("/",methods=["GET"])
def index():
    return jsonify({"api":"https://127.0.0.1:5000/ocr-api"})

@app.route("/ocr-api",methods=["GET","POST"])
def ocrapi():
    if request.method=="POST":
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        ocr_data = data(file_path)

        return jsonify({"ocr_data": ocr_data})
    return jsonify({"message":"This is the OCR API. Please send a POST request with an image."})

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)