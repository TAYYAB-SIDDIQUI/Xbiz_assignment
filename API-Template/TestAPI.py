import os
import base64
import requests
import json
from pathlib import Path

API_URL = "http://localhost:5000/document-detection"  
IMAGE_FOLDER = r"C:/image"      
SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
LOG_FILE = "ocr_results.log"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def process_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return

    image_files = [f for f in folder.iterdir() if f.suffix.lower() in SUPPORTED_EXTS]

    if not image_files:
        print("No supported image files found.")
        return

    print(f"Found {len(image_files)} image(s). Processing...\n")

    results = []

    for img_path in image_files:
        print(f"Processing: {img_path.name}")
        try:
            img_base64 = encode_image_to_base64(img_path)
            print("base64 ran successfully")
            payload = {
                #"ImageBase64": img_base64,
                "transaction_Id": img_path.stem,  
                "Category": "OCR"
            }
            print(payload)
            response = requests.post(API_URL, json=payload, timeout=60)
            print(response)
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data['transaction_Id']}")
                print(f"OCR Text:\n{data['OcrText']}\n{'-'*50}\n")

                results.append({
                    "filename": img_path.name,
                    "transaction_id": data["transaction_Id"],
                    "ocr_text": data["OcrText"],
                    "status": "success"
                })
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"Failed: {error_msg}\n{'-'*50}\n")
                results.append({
                    "filename": img_path.name,
                    "error": error_msg,
                    "status": "failed"
                })

        except Exception as e:
            print(f"Exception: {str(e)}\n{'-'*50}\n")
            results.append({
                "filename": img_path.name,
                "error": str(e),
                "status": "exception"
            })

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {LOG_FILE}")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"{success_count}/{len(image_files)} files processed successfully.")


if __name__ == "__main__":
    process_folder(IMAGE_FOLDER)