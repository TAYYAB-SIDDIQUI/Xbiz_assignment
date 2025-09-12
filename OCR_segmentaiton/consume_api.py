import requests

# URL of the Flask API
url = 'http://127.0.0.1:5000/ocr-api'

# Path to the image file you want to send for OCR
image_path = 'docs/pancard.png'

# Open the image file in binary mode
with open(image_path, 'rb') as img:
    # Prepare the files to be sent in the request
    files = {'image': img}
    
    # Send a POST request to the API with the image
    response = requests.post(url, files=files)
    
    # Check if the response is successful
    if response.status_code == 200:
        # Print the OCR result returned by the API
        ocr_data = response.json()
        print("OCR Data:", ocr_data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
