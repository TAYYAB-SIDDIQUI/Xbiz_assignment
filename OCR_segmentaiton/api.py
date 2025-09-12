import os
import cv2
from paddleocr import PaddleOCR
from flask import Flask,request,render_template,jsonify
import json
from rapidfuzz import fuzz, process

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
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    norm = cv2.divide(gray, bg, scale=255)
    cv2.imwrite("processed_images/image.png",norm)
    ocr= PaddleOCR(use_angle_cls=True,lang="en")
    ocr_hindi=PaddleOCR(use_angle_cls=True,lang="hi")
    text=ocr.ocr("processed_images/image.png")
    text_hindi=ocr_hindi.ocr("processed_images/image.png")
    list_text=text+text_hindi
    return list_text

def match_keywords_from_big_string(big_text, keywords, threshold=70):
    chunks = big_text
    matches = 0
    for chunk in chunks:
        match, score, _ = process.extractOne(chunk, keywords, scorer=fuzz.token_sort_ratio)
        if score >= threshold:
            matches += 1
            print(matches)
    return matches
def detect_document_type(text_blocks):
    print(text_blocks)
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
    "हस्ताक्षर"]     # Signature (Hindi)
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

    dl_front_keywords = [
    "Driving Licence",
    "DL No", "DL Number", "License Number", "Licence No", "Driving Licence Number",
    "Name", "Holder's Name", "Card Holder Name",
    "Father's Name", "F/O", "S/O", "D/O", "W/O",  # Relations
    "Date of Birth", "DOB", "D.O.B.",
    "Gender", "Male", "Female", "Others",
    "Address", "Permanent Address",
    "Valid Till", "Valid Upto", "Validity",
    "Valid From", "Issue Date", "Date of Issue",
    "Issuing Authority", "Transport Department",
    "Government of India", "Govt. of India",
    "Signature",
    "Photograph", "Photo",
    "Card Type",
    "QR Code",
    # Hindi equivalents (optional)
    "नाम", "पिता का नाम", "जन्म तिथि", "लिंग", "हस्ताक्षर", "पता"]
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
    bank_transaction_keywords = [
    "Date", "Txn Date", "Transaction Date",
    "Description", "Narration", "Details", "Particulars",
    "Debit", "Withdrawal", "Dr",
    "Credit", "Deposit", "Cr",
    "Balance", "Closing Balance", "Running Balance",
    "Ref No", "Cheque No", "Transaction ID",
    "Transfer", "NEFT", "RTGS", "IMPS", "UPI", "ATM", "Salary", "POS", "ACH", "NACH"]

    scores = {
    "aadhaar": match_keywords_from_big_string(text, aadhaar_front_keywords+aadhaar_back_keywords),
    "pan": match_keywords_from_big_string(text, pan_front_keywords+pan_back_keywords),
    "voter": match_keywords_from_big_string(text, voter_front_keywords+voter_back_keywords),
    "dl": match_keywords_from_big_string(text, dl_front_keywords+dl_back_keywords),
    "bank": match_keywords_from_big_string(text, bank_header_keywords+bank_transaction_keywords),
}
    print(scores)
    print("maximum",next((k for k, v in scores.items() if v == max(scores.values())), None))
    return next((k for k, v in scores.items() if v == max(scores.values())), None)

import re
# import difflib
def detect_document_sides(text_blocks,document_type):
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
            "back": []
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
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        aadhaar_front_data=extract_adhaar_text(document_sides["front"])
        #aadhaar_back_data=extract_adhaar_text(document_sides["back"])
        response={"document_type":document_type,"aadhaar_data":{"front":aadhaar_front_data,"back":document_sides["back"]}}
    elif document_type=="pan":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        pan_front_data=extract_pan_fields(document_sides["front"])
        pan_back_data=extract_pan_fields(document_sides["back"])
        response={"document_type":document_type,"front":pan_front_data,"back":document_sides["back"]}
    elif document_type=="dl":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        dl_front_data=extract_dl_fields(document_sides["front"])
        #dl_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"front":dl_front_data,"back":document_sides["back"]}
    elif document_type=="voter":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        voter_front_data=extract_voter_fields(document_sides["front"])
        #voter_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"front":voter_front_data,"back":document_sides["back"]}
    elif document_type=="bank":
        document_sides=detect_document_sides(text_input[0]["rec_texts"],document_type)
        bank_front_data=extract_bank_fields(document_sides["front"])
        #bank_back_data=extract_bank_fields(document_sides["back"])
        response={"document_type":document_type,"front":bank_front_data,"back":document_sides["back"]}
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