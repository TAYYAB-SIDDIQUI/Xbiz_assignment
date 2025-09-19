import cv2
import json
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def makeimg(json_path, input_image):
    # Input paths
    INPUT_JSON = json_path
    INPUT_IMAGE = input_image
    OUTPUT_IMAGE = "OCR_image/output_with_boxes_labels.jpg"

    # Load OCR JSON
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Safely get pages
    def get_pages(data):
        if "results" in data and data["results"]:
            result0 = data["results"][0]
            if "Data" in result0 and result0["Data"]:
                data0 = result0["Data"]
                if "responses" in data0 and data0["responses"]:
                    response0 = data0["responses"][0]
                    if "fullTextAnnotation" in response0:
                        return response0["fullTextAnnotation"].get("pages", [])
        return []

    pages = get_pages(data)

    # Load image with OpenCV
    img = cv2.imread(INPUT_IMAGE)

    # ---------------- STEP 1: Draw BOXES with OpenCV ----------------
    word_positions = []  # store positions + text
    for page in pages:
        for block in page.get("blocks", []):
            for paragraph in block.get("paragraphs", []):
                for word in paragraph.get("words", []):
                    bbox = word.get("boundingBox", {}).get("vertices", [])
                    word_text = "".join([s.get("text", "") for s in word.get("symbols", [])])

                    if bbox:
                        # Convert vertices to numpy array for cv2
                        pts = np.array([[v.get("x", 0), v.get("y", 0)] for v in bbox], np.int32)
                        pts = pts.reshape((-1, 1, 2))

                        # Draw polygon (box) in green
                        cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                        # Save word position for later text drawing
                        x, y = bbox[0].get("x", 0), bbox[0].get("y", 0)
                        word_positions.append((x, y, word_text))

    # ---------------- STEP 2: Draw TEXT with PIL (Unicode) ----------------
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # Load font (adjust to available Devanagari font on your system)
    font = ImageFont.truetype("Nirmala.ttf", 7)

    for (x, y, word_text) in word_positions:
        draw.text((x, y - 7), word_text, font=font, fill=(255, 0, 0))

    # Convert back to OpenCV
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # ---------------- STEP 3: Save final result ----------------
    cv2.imwrite(OUTPUT_IMAGE, img)
    print("✅ Image created with boxes + labels:", OUTPUT_IMAGE)

