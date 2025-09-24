import cv2
from paddleocr import PaddleOCR
def text_extraction(path):
    img = cv2.imread(path)
    blur = cv2.GaussianBlur(img, (5,5), 2)
    sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    norm = cv2.divide(gray, bg, scale=255)
    #thresh = cv2.adaptiveThreshold(norm, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11, 2)
    #thresh = cv2.threshold(bg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    # morph = cv2.morphologyEx(norm, cv2.MORPH_CLOSE, kernel)
    # coords = cv2.findNonZero(thresh)
    # angle = cv2.minAreaRect(coords)[-1]
    # if angle < -45:
    #     angle = -(90 + angle)
    # else:
    #     angle = -angle
    # (h, w) = thresh.shape[:2]
    # M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    # deskewed = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # resized = cv2.resize(deskewed, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    cv2.imwrite("processed_images/image.png",norm)
    ocr= PaddleOCR(use_angle_cls=True,lang="en",rec_batch_num=16)
    #ocr_hindi=PaddleOCR(use_angle_cls=True,lang="hi",rec_batch_num=16)
    text=ocr.ocr("processed_images/image.png")
    #text_hindi=ocr_hindi.ocr("processed_images/image.png")
    list_text=text
    return list_text