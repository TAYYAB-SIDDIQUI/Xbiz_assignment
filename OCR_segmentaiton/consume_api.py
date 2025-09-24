import requests
import os
import base64

files=os.listdir('static/docs')


# URL of the Flask API
url = 'http://127.0.0.1:5000/api_ocr_tayyab'

# Path to the image file you want to send for OCR
image_path = r"static\docs\dhapubal.png"

# Open the image file in binary mode
with open(image_path, 'rb') as img:
    # Prepare the files to be sent in the request
    payload = {'base64_image': base64.b64encode(img.read()).decode('utf-8')}
    headers = {"Content-Type": "application/json"}

    # Send a POST request to the API with the image
    response = requests.post(url, json=payload,headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        # Print the OCR result returned by the API
        ocr_data = response.json()
        print("OCR Data:", ocr_data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
