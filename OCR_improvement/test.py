import requests

# URL of your Flask OCR API
url = "http://127.0.0.1:5000/ocr"

# Path to the image you want to test
image_path = "images/pancard.jpg"  # replace with your test image path

# Open the image file in binary mode
with open(image_path, "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)

# Check response
if response.status_code == 200:
    data = response.json()
    print("OCR Response:")
    print(data)
else:
    print(f"Error {response.status_code}: {response.text}")


