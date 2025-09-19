import requests
import json
import base
import os

# API URL
def api_consume(img_path):
    url = "https://bankdevapi.digivision.ai/digivision/ai/rawtext-extraction"

    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    base64text=base.image_to_base64(img_path)
    ext = os.path.splitext(img_path)[1]
    print(ext)
    # Request payload (same as in your curl)
    payload = {
        "txnId": "TXN0000001",
        "docType": f"{ext}",
        "source": "OCR_RAW",
        "documentName": "14.JPG",
        "caseNo": "case001",
        "documentBlob": f"{base64text}"  # put base64 file content here if required
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check response
    if response.status_code == 200:
        # Save to response.json
        with open("Raw_response/response0.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
        print("✅ API response saved to response.json")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

api_consume(r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\skyamalpaul.png")