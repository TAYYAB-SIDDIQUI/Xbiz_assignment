import cv2
import json
import numpy as np

def makeimg(json_path,input_image):
# Input paths
    INPUT_JSON = json_path
    INPUT_IMAGE = input_image# Replace with your image path
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

    # Load image
    img = cv2.imread(INPUT_IMAGE)

    # Loop through pages and draw boxes + labels
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

                        # Draw polygon
                        cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                        # Place text label (above top-left corner of box)
                        x, y = bbox[0].get("x", 0), bbox[0].get("y", 0)
                        cv2.putText(img, word_text, (x, y - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

    # Save and show image
    cv2.imwrite(OUTPUT_IMAGE, img)
    print("image created")
