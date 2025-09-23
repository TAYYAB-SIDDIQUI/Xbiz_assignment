import os
import cv2
import base64
from paddleocr import PaddleOCR
from flask import Flask,request,render_template,jsonify
import json
from rapidfuzz import fuzz, process
import straight
import createbox


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp','PNG'}

# Create uploads directory if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

json_detected_file = 'detected/data.json'
if not os.path.isfile(json_detected_file):
    with open(json_detected_file, 'w') as f:
        json.dump([], f)

json_undetected_file='undetected/data.json'
if not os.path.isfile(json_undetected_file):
    with open(json_undetected_file, 'w') as f:
        json.dump([], f)

def binarytobase64(filepath):
    with open(filepath, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
    return encoded_string

def textcorrector(text_blocks,mathcing_text):
    for i,val in enumerate(text_blocks):
        mathces=process.extract(val,mathcing_text,scorer=fuzz.token_set_ratio)
        for word,score,index in mathces:
            if score>=60:
                text_blocks[i]=word
    return text_blocks

def text_extraction(path):
    img = cv2.imread(path)
    blur = cv2.GaussianBlur(img, (5,5), 2)
    sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    norm = cv2.divide(gray, bg, scale=255)
    #thresh = cv2.adaptiveThreshold(norm, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11, 2)
    #thresh = cv2.threshold(bg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    # morph = cv2.morphologyEx(norm, cv2.MORPH_CLOSE, kernel)
    # coords = cv2.findNonZero(thresh)
    # angle = cv2.minAreaRect(coords)[-1]
    # if angle < -45:
    #     angle = -(90 + angle)
    # else:
    #     angle = -angle
    # (h, w) = thresh.shape[:2]
    # M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    # deskewed = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # resized = cv2.resize(deskewed, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    cv2.imwrite("processed_images/image.png",norm)
    ocr= PaddleOCR(use_angle_cls=True,lang="en",rec_batch_num=16)
    #ocr_hindi=PaddleOCR(use_angle_cls=True,lang="hi",rec_batch_num=16)
    text=ocr.ocr("processed_images/image.png")
    #text_hindi=ocr_hindi.ocr("processed_images/image.png")
    list_text=text
    return list_text

def match_keywords_from_big_string(big_text, keywords, threshold=70):
    chunks = big_text
    matches = 0
    for chunk in chunks:
        match, score, _ = process.extractOne(chunk.lower(), keywords, scorer=fuzz.token_sort_ratio)
        if score >= threshold:
            matches += 1
    return matches
def detect_document_type(text_blocks):
    text = text_blocks
    document_type=""
    print(text)
    aadhaar_front_keywords = [
    "Aadhaar",
    "Your Aadhaar No",
    "Your Aadhaar Number",
    "Government of India",
    "Govt. of India",
    "Unique Identification Authority of India",
    "UIDAI",
    "Name",
    "नाम",
    "DOB", "Date of Birth", "D.O.B.",
    "जन्म तिथि",
    "YOB", "Year of Birth",
    "Gender", "Male", "Female", "Transgender",
    "लिंग", "पुरुष", "महिला", "ट्रांसजेंडर"]
    aadhaar_front_keywords = [s.lower() for s in aadhaar_front_keywords]
    aadhaar_back_keywords = [
    "Address",
    "पता",
    "C/O", "S/O", "D/O", "W/O",  # Care-of relations
    "District",
    "State",
    "Pin Code", "Pincode", "Postal Code",
    "India Post",
    "Mobile Number",
    "QR Code",
    "E-Aadhaar",
    "Download Aadhaar",
    "यह पहचान पत्र एक इलेक्ट्रॉनिक रूप से सत्यापित दस्तावेज़ है",  # Hindi disclaimer
    "आधार",  # "Aadhaar" in Hindi
    "भारतीय विशिष्ट पहचान प्राधिकरण",  # UIDAI in Hindi
    "Unique ID"]
    aadhaar_back_keywords= [s.lower() for s in aadhaar_back_keywords]
    pan_front_keywords = [
    "Permanent Account Number",
    "PAN",
    "PAN Number",
    "Income Tax Department",
    "Government of India",
    "Govt. of India",
    "Name",
    "Father's Name",
    "Date of Birth", "DOB", "D.O.B.",
    "Signature",
    "कारधारक का नाम",  # Name of cardholder (Hindi)
    "पिता का नाम",     # Father's name (Hindi)
    "जन्म तिथि",       # Date of Birth (Hindi)
    "हस्ताक्षर"
    ]     # Signature (Hindi)
    pan_front_keywords=[s.lower() for s in pan_front_keywords]
    pan_back_keywords = [
    "Income Tax Department",
    "Government of India",
    "Govt. of India",
    "Assessing Officer",
    "AO Code",
    "AO Type",
    "Range Code",
    "Area Code",
    "Address",
    "QR Code",
    "यह पैन कार्ड आयकर विभाग द्वारा जारी किया गया है",  # This PAN card is issued by IT Dept (Hindi)
    "यह पहचान पत्र केवल पहचान के उद्देश्य के लिए है",  # This ID is only for identification (Hindi)
    "This card is valid as identity proof only",
    "Do not laminate",
    "For Income Tax Purpose only",
    "कार्यालय का पता",  # Office address
    "पता",              # Address
    "स्थायी खाता संख्या"]  # Permanent Account Number (Hindi)
    pan_back_keywords= [s.lower() for s in pan_back_keywords]
    dl_front_keywords = [
    "Driving Licence",
    "DL No", "DL Number", "License Number", "Licence No", "Driving Licence Number",
    "Holder's Name", "Card Holder Name",
    "Date of Birth", "DOB", "D.O.B.",
    "Gender",
    "Permanent Address",
    "Valid Till", "Valid Upto", "Validity",
    "Valid From", "Issue Date", "Date of Issue",
    "Issuing Authority", "Transport Department",
    "Government of India", "Govt. of India",
    "Signature",
    "Photograph", "Photo",
    "Card Type",
    # Hindi equivalents (optional)
    "नाम", "पिता का नाम", "जन्म तिथि", "लिंग", "हस्ताक्षर", "पता"]
    dl_front_keywords= [s.lower() for s in dl_front_keywords]
    dl_back_keywords = [
    "Class of Vehicle", "Vehicle Class", "Vehicle Category", "Type of Vehicle",
    "Transport", "Non-Transport",
    "LMV", "MCWG", "HMV", "MCWOG", "TRAC", "TRANS",  # Vehicle classes
    "Authorised to Drive",
    "Valid Till", "Validity Upto", "Expiry Date",
    "Issue Date", "Effective From",
    "RTO", "Regional Transport Office",
    "Blood Group", "B+", "O+", "AB-", "A-", "Unknown",  # Blood types
    "Emergency Contact",
    "Instructions",
    "Conditions",
    "Back Side QR Code",
    "Signature of Issuing Authority",
    # Hindi (optional)
    "वाहन वर्ग", "लाइसेंस की वैधता", "रक्त समूह", "नियम और शर्तें"]
    dl_back_keywords= [s.lower() for s in dl_back_keywords]
    voter_front_keywords = [
    "Election Commission of India",
    "Electors Photo Identity Card",
    "EPIC No", "EPIC Number", "Voter ID", "Voter ID Number",
    "Name", "Card Holder Name",
    "Father's Name", "Husband's Name", "F/O", "S/O", "D/O", "W/O",
    "Date of Birth", "DOB", "D.O.B.", "Age", "YOB", "Year of Birth",
    "Gender", "Male", "Female", "Others",
    "Photograph", "Photo", "Signature",
    "Elector ID",
    "निर्वाचक फोटो पहचान पत्र",  # Elector photo identity card (Hindi)
    "नाम",  # Name
    "पिता का नाम", "पति का नाम",  # Father's/Husband's Name
    "लिंग",  # Gender
    "जन्म तिथि", "आयु"]
    voter_front_keywords= [s.lower() for s in voter_front_keywords]
    voter_back_keywords = [
    "Address",
    "House Number", "Street", "District", "State", "Pin Code", "Pincode",
    "Polling Station", "Polling Booth", "Polling Place",
    "Part Number", "Part No", "Ward Number",
    "Serial Number", "Serial No", "Voter Serial No",
    "Booth Level Officer", "BLO",
    "Constituency", "Assembly Constituency", "Parliamentary Constituency",
    "Barcode", "QR Code",
    "Disclaimers", "Note", "Instructions",
    "यह पहचान पत्र केवल पहचान के उद्देश्य के लिए है",  # This ID is for identification only (Hindi)
    "पता",  # Address
    "मतदान केंद्र",  # Polling Station
    "क्रम संख्या",  # Serial number
    "भाग संख्या",  # Part number
    "विधानसभा क्षेत्र",  # Assembly Constituency
    "निर्देश"  ]
    voter_back_keywords= [s.lower() for s in voter_back_keywords]
    bank_header_keywords = [
    "Bank Statement",
    "Account Holder",
    "Account Number", "A/C No", "A/C Number",
    "Customer ID", "CIF Number", "Customer No",
    "IFSC Code", "Branch", "Branch Code",
    "Statement Period", "From Date", "To Date",
    "Opening Balance", "Closing Balance", "Available Balance",
    "Currency", "INR", "Account Type", "Savings Account", "Current Account",
    "Bank Name", "State Bank of India", "HDFC Bank", "ICICI Bank",  # Common names
    "Email", "Phone Number", "Mobile",
    "Address"]
    bank_header_keywords= [s.lower() for s in bank_header_keywords]
    bank_transaction_keywords = [
    "Date", "Txn Date", "Transaction Date",
    "Description", "Narration", "Details", "Particulars",
    "Debit", "Withdrawal",
    "Credit", "Deposit", 
    "Balance", "Closing Balance", "Running Balance",
    "Ref No", "Cheque No", "Transaction ID",
    "Transfer", "NEFT", "RTGS", "IMPS", "UPI", "ATM", "Salary", "POS", "ACH", "NACH"]
    bank_transaction_keywords= [s.lower() for s in bank_transaction_keywords]
    scores = {
    "aadhaar": match_keywords_from_big_string(text, aadhaar_front_keywords+aadhaar_back_keywords),
    "pan": match_keywords_from_big_string(text, pan_front_keywords+pan_back_keywords),
    "voter": match_keywords_from_big_string(text, voter_front_keywords+voter_back_keywords),
    "dl": match_keywords_from_big_string(text, dl_front_keywords+dl_back_keywords),
    "bank": match_keywords_from_big_string(text, bank_header_keywords+bank_transaction_keywords),
    }
    print(scores)
    max_val = max(scores.values(), default=0)
    doc_type = "other" if max_val < 2 else next((k for k, v in scores.items() if v == max_val), "other")
    print(doc_type)
    return doc_type

import re
# import difflib
def detect_document_sides(text_blocks,document_type):
    matching_adhar=['name', 'dob', 'gender', 'male', 'female', 'uidai', 'aadhaar', 'aadhaar number', 'year of birth']
    matching_pan= ['income tax department', 'permanent account number', 'pan', 'father\'s name',
            'date of birth', 'govt. of india', 'signature']
    matching_vote=['election commission', 'voter id', 'epic', 'elector', 'father\'s name','mother\'s name', 'gender', 'dob', 'identity card']
    mathcing_dl=['driving licence', 'license number', 'dl no', 'rto', 'name', 'dob',
            'issue date', 'valid till', 'transport', 'non-transport']
    mathcing_bank=['account number', 'ifsc', 'branch', 'account holder', 'bank name', 'statement period']
    matching_list=matching_adhar+matching_pan+matching_vote+mathcing_dl+mathcing_bank
    print(textcorrector(text_blocks,matching_list))
    text = ' '.join(text_blocks).lower()
    if document_type=="aadhaar":
        has_front_keywords = any(kw in text.lower() for kw in [
            'name', 'dob', 'gender', 'male', 'female', 'uidai', 'aadhaar', 'aadhaar number', 'year of birth'
        ])

        # Aadhaar back typically includes the address and QR code
        has_back_keywords = any(kw in text.lower() for kw in [
            'address', 'care of', 'c/o', 's/o', 'd/o', 'w/o', 'pin code', 'pincode', 'mobile', 'enrollment number', 'qr code'
        ])
    elif document_type=="pan":
        
        has_front_keywords = any(kw in text.lower() for kw in [
            'income tax department', 'permanent account number', 'pan', 'father\'s name',
            'date of birth', 'govt. of india', 'signature'
        ])

        has_back_keywords = any(kw in text.lower() for kw in [
            'assessment year', 'issuing authority', 'barcode', 'qr code'
        ])
    elif document_type=='voter':
        has_front_keywords = any(kw in text.lower() for kw in [
            'election commission', 'voter id', 'epic', 'elector', 'father\'s name',
            'mother\'s name', 'gender', 'dob', 'identity card'
        ])

        has_back_keywords = any(kw in text.lower() for kw in [
            'address', 'polling station', 'assembly constituency', 'part number', 'serial number'
        ])
    elif document_type=="dl":
        has_front_keywords = any(kw in text.lower() for kw in [
            'driving licence', 'license number', 'dl no', 'rto', 'name', 'dob',
            'issue date', 'valid till', 'transport', 'non-transport'
        ])

        has_back_keywords = any(kw in text.lower() for kw in [
            'address', 'blood group', 'barcode', 'qr code', 'authorized vehicles', 'emergency contact'
        ])
    elif document_type=="bank":
        has_front_keywords = any(kw in text.lower() for kw in [
            'account number', 'ifsc', 'branch', 'account holder', 'bank name', 'statement period'
        ])

        has_back_keywords = any(kw in text.lower() for kw in [
            'transaction', 'debit', 'credit', 'balance', 'neft', 'rtgs', 'upi', 'imps', 'description'
        ])
    elif document_type=="other":
        keywords=[]
        

    #doc_type = detect_document_type(text)
    # Smart classification
    if has_front_keywords and has_back_keywords:
        return {
            "front": text_blocks,
            "back": text_blocks
        }
    elif has_front_keywords:
        return {
            "front": text_blocks,
            "back": []
        }
    elif has_back_keywords:
        return {
            "front": [],
            "back": text_blocks
        }
    else:
        return {
            "front": [],
            "back": [],
            "document detected as other":text_blocks
        }


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
        match_gender=process.extract(block_lower,["male","female"],scorer=fuzz.token_set_ratio)
        for word, score, _ in match_gender:
            if score >= 90:
                fields["gender"] = word.upper()
                print("matched", word, "with score", score)
                break

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

    for i,block in enumerate(ocr_blocks):
        text = block.strip()
        # PAN Number: e.g., ABCDE1234F
        clean_text = re.sub(r'[^A-Z0-9]', '', text)
        clean_text=clean_text.upper()
        pan_match = re.search(r'[A-Z]{5}\d{4}[A-Z]', clean_text)
        if pan_match:
            fields['pan_number'] = pan_match.group()

        # DOB
        dob_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        if dob_match:
            fields['dob'] = dob_match.group()

        # Fuzzy matching for Father and Name
        match_fathername=process.extract(block,["Father's","Fathers name","Father's name"],scorer=fuzz.token_set_ratio)
        for word, score, _ in match_fathername:
            if score >= 80:
                fields["father_name"] = ocr_blocks[i+1]
                print("matched", word, "with score", score)
        
        match_name=process.extract(block,["Name","names","name of"],scorer=fuzz.token_set_ratio)
        for word, score, _ in match_name:
            if score >= 80:
                fields["name"] = ocr_blocks[i+1]
                print("matched", word, "with score", score)

    fields['is_valid_pan'] = fields['pan_number'] is not None
    return fields

def extract_voter_fields(ocr_blocks):
    fields = {
        'voter_id': None,
        'father name':None,
        'name': None,
        'gender': None,
        'dob': None,
        'is_valid_voter': False
    }

    for i,block in enumerate(ocr_blocks):
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
        matches=process.extractOne("name",ocr_blocks)
        if matches[1]>=80:
            name=matches[0]
        else:
            name=text
                

        if "name" in text.lower():
            fields['name'] = name

        if "father's name" in text.lower():
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

    for i,block in enumerate(ocr_blocks):
        text = block.strip()

        # Account number pattern
        if "account number" in block.lower():
            match=ocr_blocks[i]
            pass
        acc_match = re.search(r'\d{9,18}', text)
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

def data(path):
    id=0
    t_id=f"T{id}"
    id+=1
    angle=straight.compute_text_angle_for_best_word(path,draw_result=False)
    img_path=straight.rotate_image_auto(path,angle)
    text_input=text_extraction(img_path)
    text_boxes=text_input[0]["rec_boxes"].tolist()
    print(text_boxes)
    if angle and img_path and text_input and text_boxes:
        remark="Success"
    else:
        remark="failed"
    createbox.draw_easyocr_boxes(img_path,"output.jpg")
    document_type=detect_document_type(text_input[0]["rec_texts"])
    print(document_type)
    if document_type=="aadhaar":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        aadhaar_front_data=extract_adhaar_text(document_sides["front"])
        #aadhaar_back_data=extract_adhaar_text(document_sides["back"])
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"front":aadhaar_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="pan":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        pan_front_data=extract_pan_fields(document_sides["front"])
        pan_back_data=extract_pan_fields(document_sides["back"])
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"front":pan_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="dl":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        dl_front_data=extract_dl_fields(document_sides["front"])
        #dl_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"front":dl_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="voter":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        voter_front_data=extract_voter_fields(document_sides["front"])
        #voter_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"front":voter_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="bank":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        bank_front_data=extract_bank_fields(document_sides["front"])
        #bank_back_data=extract_bank_fields(document_sides["back"])
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"front":bank_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="other":
        response={"document_type":document_type,"base64":binarytobase64(path),"ocr_result":[{"raw_text":text_input[0]["rec_texts"],"boundingbox":text_boxes}]}
        try:
            with open(json_undetected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_undetected_file, 'w') as f:
            json.dump(data, f, indent=2,ensure_ascii=False)
        return response

    else:
        response={"document_type":"other","base64":binarytobase64(path),"ocr_result":[{"raw":text_input[0]["rec_texts"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
        try:
            with open(json_undetected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_undetected_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return response
    if document_type!="other":
        try:
            with open(json_detected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_detected_file, 'w') as f:
            json.dump(data, f, indent=2,ensure_ascii=False)
        return response

# for i in os.listdir("docs"):
#     print(data(f"docs/{i}"))

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ocr",methods=["GET","POST"])
def ocrapi():
    if request.method == "POST":
        if 'images' not in request.files:
            return jsonify({"error": "No images part in the request"}), 400

        files = request.files.getlist("images")

        if not files:
            return jsonify({"error": "No selected files"}), 400

        all_results_html = ""
        for file in files:
            if file and allowed_file(file.filename):
                file_path = os.path.join('uploads', file.filename)
                file.save(file_path)

                ocr_data = data(file_path)
                html_str = "<div style='font-family: Arial; line-height: 1.6;'>"
                doc_type = ocr_data.get("document_type", "Unknown")
                html_str += f"<h2>🧾 Document Type: {doc_type.upper()}</h2><hr>"

                def format_dict_section(title, section_dict):
                    section_html = f"<h3>{title}</h3><div style='margin-left: 15px;'>"
                    if isinstance(section_dict, dict):
                        for key, value in section_dict.items():
                            key_fmt = key.replace('_', ' ').capitalize()
                            if key_fmt=="Raw blocks":
                                continue
                            if isinstance(value, list):
                                section_html += f"<strong>{key_fmt}:</strong><br>"
                                for item in value:
                                    section_html += f"&nbsp;&nbsp;- {item}<br>"
                            elif isinstance(value, dict):
                                for i in value:
                                    section_html += f"<label>{i}:</label> <span>{value[i]}</span><br>"
                            else:
                                section_html += f"<strong>{key_fmt}:</strong> {value}<br>"
                    elif isinstance(section_dict, list):
                        for item in section_dict:
                            section_html += f"{item}<br>"
                    section_html += "</div><br>"
                    return section_html

                for key, value in ocr_data.items():
                    if key == "document_type":
                        continue
                    elif key == "front":
                        html_str += format_dict_section("📄 FRONT SIDE", value)
                    elif key == "back":
                        html_str += format_dict_section("📄 BACK SIDE", value)
                    else:
                        html_str += format_dict_section(key.capitalize(), value)

                html_str += "</div><hr><br>"
                # Wrap each card
                card_html = f"""
                <div class="card mb-4 shadow">
                    <div class="card-body">
                        <h5 class="card-title">Processed File: {file.filename}</h5>
                        <img src='data:image/jpeg;base64,{binarytobase64(f"static/docs/{file.filename}")}' class="img-fluid mb-3" alt="{file.filename}">
                        {html_str}
                    </div>
                </div>
                """
                all_results_html += card_html

        return render_template("data.html", data=all_results_html)
    else:
        return jsonify({"error": "Method is GET"})
@app.route("/allocr", methods=["GET","POST"])
def allocr():

    folder="static/docs/"
    file_names=os.listdir("static/docs")
    all_results_html=""
    for i in file_names:
        file_path=folder+i
        ocr_data=data(file_path)
        html_str = "<div style='font-family: Arial; line-height: 1.6;'>"
        doc_type = ocr_data.get("document_type", "Unknown")
        html_str += f"<h2>🧾 Document Type: {doc_type.upper()}</h2><hr>"

        def format_dict_section(title, section_dict):
            section_html = f"<h3>{title}</h3><div style='margin-left: 15px;'>"
            if isinstance(section_dict, dict):
                for key, value in section_dict.items():
                    key_fmt = key.replace('_', ' ').capitalize()
                    if key_fmt=="Raw blocks":
                        continue
                    if isinstance(value, list):
                        section_html += f"<strong>{key_fmt}:</strong><br>"
                        for item in value:
                            section_html += f"&nbsp;&nbsp;- {item}<br>"
                    elif isinstance(value, dict):
                        for i in value:
                            section_html += f"<label>{i}:</label> <span>{value[i]}</span><br>"
                    else:
                        section_html += f"<strong>{key_fmt}:</strong> {value}<br>"
            elif isinstance(section_dict, list):
                for item in section_dict:
                    section_html += f"{item}<br>"
            section_html += "</div><br>"
            return section_html

        for key, value in ocr_data.items():
            if key == "document_type":
                continue
            elif key == "front":
                html_str += format_dict_section("📄 FRONT SIDE", value)
            elif key == "back":
                html_str += format_dict_section("📄 BACK SIDE", value)
            else:
                html_str += format_dict_section(key.capitalize(), value)

        html_str += "</div><hr><br>"
        # Wrap each card
        card_html = f"""
        <div class="card mb-4 shadow">
            <div class="card-body">
                <h5 class="card-title">Processed File: {i}</h5>
                <img src='data:image/jpeg;base64,{binarytobase64(f"static/docs/{i}")}' class="img-fluid mb-3" alt="{i}">
                {html_str}
            </div>
        </div>
        """
        all_results_html += card_html
    return render_template("data.html",data=all_results_html)


if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)