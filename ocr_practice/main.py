# import cv2
# import matplotlib.pyplot as plt
# import numpy as np

# img=cv2.imread("image.png")
# img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

# plt.figure(figsize=(10,10))

# plt.subplot(2,2,1)
# plt.title("original")
# plt.imshow(img)

# plt.subplot(2,2,2)
# gblur=cv2.GaussianBlur(img,(1,1),0)
# sharpen_kernel = np.array([[0, -0.3,  0],
#                            [-0.3, 2.5, -0.3],
#                            [0, -0.3,  0]])
# gsharpened = cv2.filter2D(gblur, -1, sharpen_kernel)
# plt.title("Gaussain blur")
# plt.imshow(gsharpened)

# plt.subplot(2,2,3)
# plt.title("NLM blur")
# mlnblur=cv2.fastNlMeansDenoisingColored(img,3,1,7)
# sharpen_kernel = np.array([[0, -0.3,  0],
#                            [-0.3, 2.5, -0.3],
#                            [0, -0.3,  0]])
# mlnsharpened = cv2.filter2D(mlnblur, -1, sharpen_kernel)
# plt.imshow(mlnsharpened)

# plt.subplot(2,2,4)
# gblur=cv2.GaussianBlur(img,(1,1),0)
# sharpen_kernel = np.array([[0, -0.5,  0],
#                            [-0.5, 3, -0.5],
#                            [0, -0.5,  0]])
# gsharpened = cv2.filter2D(gblur, -1, sharpen_kernel)
# mln_gblur=cv2.fastNlMeansDenoisingColored(img,3,1,21)
# nml_sharp=cv2.filter2D(mln_gblur,-1,sharpen_kernel)


# plt.title("Gaussain + nlm blur")
# plt.imshow(mln_gblur)
# plt.tight_layout()
# plt.show()


# import cv2
# import pytesseract

# # Load image
# img = cv2.imread("image.png")

# # Convert to RGB (Tesseract prefers RGB)
# rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# # Get OCR data with bounding boxes
# data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)

# # Loop through each detected block
# n_boxes = len(data['level'])
# for i in range(n_boxes):
#     (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
#     text = data['text'][i]
    
#     # Draw rectangle around each block
#     if text.strip() != "":
#         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

# # Save or display the result
# cv2.imwrite("output_with_blocks.jpg", img)
# # cv2.imshow("Detected Blocks", img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()

import cv2
import numpy as np
from paddleocr import PaddleOCR

# Initialize PaddleOCR model (use lang='en' for English)
ocr = PaddleOCR(use_angle_cls=True, lang='en') 

# Read image
img_path = "pancard.png"
img = cv2.imread(img_path)

# Run OCR - get results with boxes and texts
result = ocr.ocr(img_path)

# Loop over each detected text box
rec_texts = result[0]["rec_texts"]
rec_boxes = result[0]["rec_boxes"]
def createboxes(img,rec_texts,rec_boxes):
    img=cv2.imread(img)
    rectangle=[]
    for text, box in zip(rec_texts, rec_boxes):
        pt1=[int(box[0]),int(box[1])]
        pt2=[int(box[2]),int(box[3])]
        x_min = min(pt1[0], pt2[0])
        x_max = max(pt1[0], pt2[0])
        y_min = min(pt1[1], pt2[1])
        y_max = max(pt1[1], pt2[1])

        rectangle=[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        print(rectangle)
        pts = np.array(rectangle, dtype=np.int32)

        # Reshape for polylines: needs shape (number_of_points, 1, 2)
        pts = pts.reshape((-1, 1, 2))

        # Draw the polygon (rectangle) on the image
        cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            

    cv2.imwrite("bimg.png",img)
    print("img created")