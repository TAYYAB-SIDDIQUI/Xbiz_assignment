import cv2
import easyocr
import numpy as np

def draw_easyocr_boxes(image_path, output_path="easyocr_output.png"):
    # Initialize EasyOCR reader (English in this example)
    reader = easyocr.Reader(['en'])

    # Read the image
    img = cv2.imread(image_path)

    # Run OCR
    results = reader.readtext(image_path)

    # Loop through detections
    for (bbox, text, prob) in results:
        # bbox contains 4 corner points [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        pts = [(int(x), int(y)) for x, y in bbox]

        # Draw polygon around detected text
        cv2.polylines(img, [np.array(pts, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        # Put the text label above the top-left corner
        x, y = pts[0]
        cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2, cv2.LINE_AA)

    # Save annotated image
    cv2.imwrite(output_path, img)
    print(f"OCR result saved as {output_path}")

# Example usage:
# draw_easyocr_boxes(r"straight_image.png", "output_easyocr.png")
