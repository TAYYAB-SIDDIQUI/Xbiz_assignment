import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        # Read the image and encode it to base64
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    return encoded_string

