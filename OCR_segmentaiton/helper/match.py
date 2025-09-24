from rapidfuzz import process,fuzz
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