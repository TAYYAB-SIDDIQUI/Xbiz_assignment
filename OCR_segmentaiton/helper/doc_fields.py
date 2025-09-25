import re
from rapidfuzz import process,fuzz
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
        'raw_blocks': ocr_blocks,
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
        'raw_blocks': ocr_blocks,
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
        'raw_blocks': ocr_blocks,
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
        'raw_blocks': ocr_blocks,
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