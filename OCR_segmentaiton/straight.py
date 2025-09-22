import cv2
import numpy as np
import math
import easyocr
import matplotlib.pyplot as plt

reader = easyocr.Reader(['en'])  # initialize once

def compute_text_angle_for_best_word_easyocr(img_path, draw_result=True):
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Can't open {img_path}")
    h_img, w_img = img.shape[:2]

    # Preprocessing
    blur = cv2.GaussianBlur(img, (5,5), 2)
    sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(gray, 31)
    img_proc = cv2.divide(gray, bg, scale=255)

    # Use EasyOCR to get bounding boxes
    results = reader.readtext(img_proc)
    if not results:
        raise RuntimeError("No text detected by EasyOCR")

    # Pick the word box with largest area
    best_box = None
    best_area = 0
    for bbox, text, prob in results:
        # bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        x_coords = [pt[0] for pt in bbox]
        y_coords = [pt[1] for pt in bbox]
        left, top = int(min(x_coords)), int(min(y_coords))
        width, height = int(max(x_coords)-left), int(max(y_coords)-top)
        area = width * height
        if area > best_area:
            best_area = area
            best_box = (left, top, width, height)

    left, top, width, height = best_box
    pad = 8
    left = max(0, left - pad)
    top = max(0, top - pad)
    width = min(w_img - left, width + 2*pad)
    height = min(h_img - top, height + 2*pad)
    crop = img[top:top+height, left:left+width].copy()

    # Make mask for text
    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = 255 - thresh if cv2.countNonZero(thresh) > thresh.size/2 else thresh
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Fit line on text pixels to find angle
    ys, xs = np.where(mask > 0)
    if len(xs) < 2:
        raise RuntimeError("Not enough pixels to compute angle")
    pts = np.column_stack((xs, ys)).astype(np.float32).reshape(-1,1,2)
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01).flatten()
    angle_rad = math.atan2(vy, vx)
    angle_deg = abs(math.degrees(angle_rad))
    if angle_deg > 90:
        angle_deg = 180.0 - angle_deg

    # Optional: annotate
    out = img.copy()
    cv2.rectangle(out, (left, top), (left+width, top+height), (200,200,0), 2)
    L = max(width, height) * 2
    p1 = (int(x0 - vx*L) + left, int(y0 - vy*L) + top)
    p2 = (int(x0 + vx*L) + left, int(y0 + vy*L) + top)
    cv2.line(out, p1, p2, (255,0,0), 2)
    cv2.imwrite("annotated_out_easyocr.png", out)

    print(f"Detected angle: {angle_deg:.2f}°")
    return angle_deg

def rotate_image_auto(image_path, angle):
        """
        Rotate image automatically based on the detected tilt angle.
        If angle > 0, rotates clockwise to deskew.
        If angle < 0, rotates counter-clockwise to deskew.
        """
        print(image_path)
        img=cv2.imread(image_path)
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)

        # Always rotate opposite to detected angle
        final_angle = -angle
        print(final_angle)
        M = cv2.getRotationMatrix2D(center, final_angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)
        output_path="straight_image.png"
        cv2.imwrite(output_path,rotated)
        return output_path
# if __name__ == "__main__":
#     img_path = r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\dhapubal.png"# change to your file
#     angle = compute_text_angle_for_best_word(img_path, draw_result=False)
#     rotate_image_auto(img_path,angle)
#     print("Saved annotated image to annotated_out.png")
#     print("Angle (degrees):", angle)
