def detect_document_sides(text_blocks,document_type):
    matching_adhar=['name', 'dob', 'gender', 'male', 'female', 'uidai', 'aadhaar', 'aadhaar number', 'year of birth']
    matching_pan= ['income tax department', 'permanent account number', 'pan', 'father\'s name',
            'date of birth', 'govt. of india', 'signature']
    matching_vote=['election commission', 'voter id', 'epic', 'elector', 'father\'s name','mother\'s name', 'gender', 'dob', 'identity card']
    mathcing_dl=['driving licence', 'license number', 'dl no', 'rto', 'name', 'dob',
            'issue date', 'valid till', 'transport', 'non-transport']
    mathcing_bank=['account number', 'ifsc', 'branch', 'account holder', 'bank name', 'statement period']
    matching_list=matching_adhar+matching_pan+matching_vote+mathcing_dl+mathcing_bank
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