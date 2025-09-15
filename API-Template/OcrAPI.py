from flask import Flask, request, jsonify
import base64
import json
import os
import uuid
import time
from datetime import datetime
from PIL import Image
import io
from paddleocr import PaddleOCR

app = Flask(__name__)

OCR_OUTPUT_DIR = "ocr_output"
os.makedirs(OCR_OUTPUT_DIR, exist_ok=True)

ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

def get_request():
    mimetype = request.mimetype
    form = {}
    try:
        if mimetype == 'application/x-www-form-urlencoded':
            raw = next(iter(request.form.keys()))
            form = json.loads(raw)
        elif mimetype == 'multipart/form-data':
            form = dict(request.form)
        elif mimetype == 'application/json':
            form = request.get_json()
        else:
            data = request.data.decode('utf-8', errors='ignore')
            if data.strip():
                try:
                    form = json.loads(data)
                except json.JSONDecodeError:
                    form = {"raw_data": data}
            else:
                form = {}
    except Exception as e:
        form = {"error": f"Failed to parse request: {str(e)}"}

    if not form:
        form = {}
    return form

def generate_unique_transaction_id(base_id):
    timestamp = int(time.time())
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{base_id}_{timestamp}_{unique_suffix}"

@app.route('/home')
def hello():
	return "<html><body style='text-align:center; font-family:sans-serif; font-size:2rem; color:#4CAF50;'>API RUNNING FOR DOCUMENT DETECTION</body></html>"

@app.route('/document-detection', methods=['POST'])
def ocr_endpoint():
    try:
        data = get_request()

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid request format"}), 400

        image_base64 = data.get("ImageBase64")
        transaction_id = data.get("transaction_Id")
        category = data.get("Category")

        if not image_base64:
            return jsonify({"error": "ImageBase64 is required"}), 400
        if not transaction_id:
            return jsonify({"error": "transaction_Id is required"}), 400
        if category != "OCR":
            return jsonify({"error": "Category must be 'OCR'"}), 400

        unique_transaction_id = generate_unique_transaction_id(transaction_id)

        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({"error": f"Invalid base64 image: {str(e)}"}), 400

        try:
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            temp_image_path = os.path.join(OCR_OUTPUT_DIR, f"{unique_transaction_id}_temp.jpg")
            image.save(temp_image_path, format='JPEG')
        except Exception as e:
            return jsonify({"error": f"Cannot process image: {str(e)}"}), 400

        try:
            result = ocr_engine.ocr(temp_image_path)
            os.remove(temp_image_path)

            ocr_lines = []
            import pdb
            pdb.set_trace()
            if result and len(result) > 0:
                ocr_lines+=result[0]["rec_texts"]
                print(ocr_lines)

            ocr_text = "\n".join(ocr_lines).strip()
        except Exception as e:
            if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500

        filename = f"{unique_transaction_id}.txt"
        filepath = os.path.join(OCR_OUTPUT_DIR, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(ocr_text)
        except Exception as e:
            return jsonify({"error": f"Failed to save OCR text: {str(e)}"}), 500

        response = {
            #"InputImageBase64": image_base64,
            "transaction_Id": unique_transaction_id,
            "OcrText": ocr_text,
            "DocumentType": ""
        }

        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
