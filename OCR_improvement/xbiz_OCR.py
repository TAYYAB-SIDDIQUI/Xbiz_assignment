from paddleocr import PaddleOCR
import easyocr
import cv2
import os
from flask import Flask, request, jsonify
import json
import base64

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('noise_images', exist_ok=True)

app = Flask(__name__)

def OCR_processed(path):
    noise_images_path = "noise_images/"
    
    # Read and convert image
    noise_img = cv2.imread(path)
    if noise_img is None:
        return "Error: Image not found", "", "", ""
    noise_img = cv2.cvtColor(noise_img, cv2.COLOR_BGR2RGB)

    # Denoising and sharpening
    blur = cv2.GaussianBlur(noise_img, (5,5), 2)
    sharp = cv2.addWeighted(noise_img, 1.5, blur, -0.5, 0)
    denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)

    # Grayscale and background normalization
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    norm = cv2.divide(gray, bg, scale=255)

    # Save processed image
    processed_path = os.path.join(noise_images_path, "processed.jpg")
    cv2.imwrite(processed_path, norm)

    # Initialize OCR engines
    easy_ocr = easyocr.Reader(['en'])
    paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # OCR results
    easyocr_result = easy_ocr.readtext(path)
    easyocr_result_pr = easy_ocr.readtext(processed_path)

    easy_ocr_texts_pr = " ".join([t[1] for t in easyocr_result_pr])
    easy_ocr_texts = " ".join([t[1] for t in easyocr_result])

    paddle_result_pr = paddle_ocr.ocr(processed_path)
    paddle_result = paddle_ocr.ocr(path)

    text_pr = " ".join(paddle_result_pr[0]["rec_texts"])
    text = " ".join(paddle_result[0]["rec_texts"])

    # Save output to file
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text_pr + "\n")
        f.write(text + "\n")
        f.write(easy_ocr_texts_pr + "\n")
        f.write(easy_ocr_texts + "\n")

    return text_pr, text, easy_ocr_texts_pr, easy_ocr_texts

@app.route("/ocr", methods=['POST','GET'])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_path = os.path.join('uploads', image_file.filename)
    image_file.save(image_path)

    # Process uploaded image
    paddle_processed, paddle, easy_processed, easy = OCR_processed(image_path)
    with open(image_path ,"rb") as img_file:
        encoded_string=base64.b64encode(img_file.read()).decode("utf-8")
    response = {
        "input_image_base64": encoded_string,
        "PaddleOCR_ocr_response": paddle,
        "EasyOCR_ocr_response": easy
    }
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(response,f,indent=4)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
