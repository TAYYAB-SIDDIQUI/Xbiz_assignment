# import cv2
# import numpy as np
# import pytesseract
# import math
# from pytesseract import Output
# import matplotlib.pyplot as plt

# # If tesseract isn't in PATH, uncomment and set:
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# def compute_text_angle_for_best_word(img_path, draw_result=True):
#     img = cv2.imread(img_path)
#     # blur = cv2.GaussianBlur(img, (5,5), 2)
#     # sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
#     # denoised = cv2.fastNlMeansDenoisingColored(sharp, None, 6, 10, 9, 21)
#     # gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
#     # bg = cv2.medianBlur(gray, 31)
#     # img = cv2.divide(gray, bg, scale=255)
#     if img is None:
#         raise FileNotFoundError(f"Can't open {img_path}")
#     h_img, w_img = img.shape[:2]

#     # get word boxes from pytesseract
#     data = pytesseract.image_to_data(img, output_type=Output.DICT)
#     n_boxes = len(data['level'])
#     # pick the word box with the largest width*height (robust choice)
#     best_idx = None
#     best_area = 0
#     for i in range(n_boxes):
#         text = data['text'][i].strip()
#         if text == "":
#             continue
#         left = data['left'][i]
#         top = data['top'][i]
#         width = data['width'][i]
#         height = data['height'][i]
#         area = width * height
#         if area > best_area:
#             best_area = area
#             best_idx = i

#     if best_idx is None:
#         raise RuntimeError("No text boxes detected by pytesseract.")

#     # Extract the chosen box (with a small padding)
#     pad = 1
#     left = max(0, data['left'][best_idx] - pad)
#     top = max(0, data['top'][best_idx] - pad)
#     width = min(w_img - left, data['width'][best_idx] + pad)
#     height = min(h_img - top, data['height'][best_idx] + pad)
#     crop = img[top:top+height, left:left+width].copy()
#     gray=cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY)
#     # Preprocess crop to get text mask (foreground white, background black)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     # Make mask so text is white (non-zero)
#     # If background is white (most pixels white), invert so text is white
#     if cv2.countNonZero(thresh) > thresh.size / 2:
#         mask = 255 - thresh
#     else:
#         mask = thresh

#     # Remove small noise
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

#     angle_deg = None
#     used_method = None
#     fitted_line_pts = None

#     # Method 1: fitLine on mask pixel coords
#     ys, xs = np.where(mask > 0)
#     if len(xs) >= 2:
#         pts = np.column_stack((xs, ys)).astype(np.float32).reshape(-1,1,2)  # shape (N,1,2)
#         vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01).flatten()
#         # angle relative to horizontal in degrees
#         angle_rad = math.atan2(vy, vx)
#         angle_deg = abs(math.degrees(angle_rad))
#         if angle_deg > 90:
#             angle_deg = 180.0 - angle_deg
#         used_method = 'fitLine'
#         # produce two points for drawing (in crop coords)
#         L = max(width, height) * 2
#         p1 = (int(x0 - vx * L), int(y0 - vy * L))
#         p2 = (int(x0 + vx * L), int(y0 + vy * L))
#         fitted_line_pts = (p1, p2)
#     else:
#         # Method 2: try HoughLinesP on edges
#         edges = cv2.Canny(mask, 50, 150, apertureSize=3)
#         lines = cv2.HoughLinesP(edges, 1, np.pi/180.0, threshold=20, minLineLength=max(10, min(width, height)//4), maxLineGap=10)
#         if lines is not None and len(lines) > 0:
#             # compute length-weighted average angle
#             angles = []
#             lengths = []
#             for l in lines:
#                 x1,y1,x2,y2 = l[0]
#                 dx = x2 - x1
#                 dy = y2 - y1
#                 ang = math.degrees(math.atan2(dy, dx))
#                 length = math.hypot(dx, dy)
#                 angles.append(ang)
#                 lengths.append(length)
#             # weighted average
#             ang_avg = np.average(np.array(angles), weights=np.array(lengths))
#             angle_deg = abs(ang_avg)
#             if angle_deg > 90:
#                 angle_deg = 180.0 - angle_deg
#             used_method = 'hough'
#             # pick the longest line to draw
#             longest = max(lines, key=lambda ln: math.hypot(ln[0][2]-ln[0][0], ln[0][3]-ln[0][1]))[0]
#             fitted_line_pts = ((longest[0], longest[1]), (longest[2], longest[3]))
#         else:
#             # Method 3: fallback to minAreaRect on largest contour
#             contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             if contours:
#                 largest = max(contours, key=cv2.contourArea)
#                 if cv2.contourArea(largest) > 5:
#                     rect = cv2.minAreaRect(largest)  # ((cx,cy),(w,h),angle)
#                     rect_w, rect_h = rect[1][0], rect[1][1]
#                     rect_angle = rect[2]
#                     # normalize angle to angle from horizontal
#                     if rect_w < rect_h:
#                         angle = rect_angle + 90.0
#                     else:
#                         angle = rect_angle
#                     angle_deg = abs(angle)
#                     if angle_deg > 90:
#                         angle_deg = 180.0 - angle_deg
#                     used_method = 'minAreaRect'
#                     # compute a drawing line from the rectangle center and angle
#                     cx, cy = rect[0]
#                     theta = math.radians(angle)
#                     L = max(width, height) * 2
#                     p1 = (int(cx - math.cos(theta)*L), int(cy - math.sin(theta)*L))
#                     p2 = (int(cx + math.cos(theta)*L), int(cy + math.sin(theta)*L))
#                     fitted_line_pts = (p1, p2)

#     if angle_deg is None:
#         raise RuntimeError("Couldn't determine text orientation in the selected box.")

#     # Choose a horizontal line at any y point inside crop: we'll use crop center y (you can change this)
#     chosen_y_in_crop = height // 2  # change if you want a different y
#     horiz_pt1 = (0, chosen_y_in_crop)
#     horiz_pt2 = (width, chosen_y_in_crop)

#     # Draw on a copy of the original image (offset the fitted line by left,top)
#     out = img.copy()
#     # box rectangle for visual
#     cv2.rectangle(out, (left, top), (left+width, top+height), (200,200,0), 2)

#     # draw horizontal line (green)
#     cv2.line(out, (left + horiz_pt1[0], top + horiz_pt1[1]), (left + horiz_pt2[0], top + horiz_pt2[1]), (0,255,0), 2)

#     # draw fitted (tilted) line (blue)
#     p1, p2 = fitted_line_pts
#     cv2.line(out, (left + p1[0], top + p1[1]), (left + p2[0], top + p2[1]), (255,0,0), 2)

#     # draw a small marker at chosen y in the crop center
#     cv2.circle(out, (left + width//2, top + chosen_y_in_crop), 4, (0,255,255), -1)
#     cv2.imwrite("processed_images/annotated_image.png",out)
#     # Report angle between the horizontal and fitted line
#     angle_between = angle_deg+1  # already absolute angle from horizontal in degrees
#     print(f"Used method: {used_method}")
#     print(f"Angle between horizontal and text line: {angle_between:.2f}°")
    

#     # Example usage:
#     # img = cv2.imread(img_path)
#     # rotated = rotate_image_auto(img, angle_between)  # rotate image by -15 degrees
#     # plt.imshow(rotated)
#     # plt.show()

#     # if draw_result:
#     #     # show in a window (may not work in headless environments)
#     #     plt.imshow(img)
#     #     plt.show()

#     # if save_out:
#     #     cv2.imwrite(save_out)

#     return angle_between
# def rotate_image_auto(image_path, angle):
#         """
#         Rotate image automatically based on the detected tilt angle.
#         If angle > 0, rotates clockwise to deskew.
#         If angle < 0, rotates counter-clockwise to deskew.
#         """
#         print(image_path)
#         img=cv2.imread(image_path)
#         (h, w) = img.shape[:2]
#         center = (w // 2, h // 2)

#         # Always rotate opposite to detected angle
#         final_angle = -angle
#         print(final_angle)
#         M = cv2.getRotationMatrix2D(center, final_angle, 1.0)
#         rotated = cv2.warpAffine(img, M, (w, h),
#                                 flags=cv2.INTER_CUBIC,
#                                 borderMode=cv2.BORDER_REPLICATE)
#         output_path="processed_images/straight_image.png"
#         cv2.imwrite(output_path,rotated)
#         return output_path
# # if __name__ == "__main__":
# #     img_path = r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\dhapubal.png"# change to your file
# #     angle = compute_text_angle_for_best_word(img_path, draw_result=False)
# #     rotate_image_auto(img_path,angle)
# #     print("Saved annotated image to annotated_out.png")
# #     print("Angle (degrees):", angle)
import cv2
import numpy as np
import math
import easyocr
import cv2
import numpy as np
import math

def compute_skew_projection(img_path, delta=0.5, limit=15):
    """
    Detect skew angle of text using projection profile analysis.
    delta = step size in degrees
    limit = max search angle (±limit degrees)
    """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Can't open {img_path}")

    # Binarize (text = black)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(thresh) > 127:
        thresh = 255 - thresh  # ensure text is black

    best_angle = 0
    max_var = -1

    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        # Rotate small angle
        M = cv2.getRotationMatrix2D((thresh.shape[1]//2, thresh.shape[0]//2), angle, 1)
        rotated = cv2.warpAffine(thresh, M, (thresh.shape[1], thresh.shape[0]),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Projection profile (sum of pixels per row)
        proj = np.sum(rotated, axis=1)
        var = np.var(proj)  # variance = sharpness of text lines

        if var > max_var:
            max_var = var
            best_angle = angle

    print(f"Detected skew angle: {best_angle:.2f}°")
    return best_angle


def rotate_image_auto(image_path, angle):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Can't open {image_path}")

    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)

    if abs(angle) < 0.5:  # tolerance
        print("Image already straight.")
        return image_path
    print("final_angle :",-angle)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    out_path = "processed_images/straight_image.png"
    cv2.imwrite(out_path, rotated)
    return out_path

# def compute_text_angle_for_best_word(img_path, tolerance=3,draw_result=False):
#     img = cv2.imread(img_path)
#     if img is None:
#         raise FileNotFoundError(f"Can't open {img_path}")

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # OCR just to get a text region
#     reader = easyocr.Reader(['en'])
#     results = reader.readtext(gray)

#     if len(results) == 0:
#         raise RuntimeError("No text detected.")

#     # Pick largest box
#     best_area, best_bbox = 0, None
#     for (bbox, text, conf) in results:
#         xs = [pt[0] for pt in bbox]
#         ys = [pt[1] for pt in bbox]
#         left, top, right, bottom = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
#         area = (right - left) * (bottom - top)
#         if area > best_area and text.strip():
#             best_area, best_bbox = area, (left, top, right, bottom)

#     if best_bbox is None:
#         raise RuntimeError("No valid OCR box found.")

#     left, top, right, bottom = best_bbox
#     crop = gray[top:bottom, left:right]

#     # Threshold text region
#     _, thresh = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     if cv2.countNonZero(thresh) > thresh.size / 2:
#         mask = 255 - thresh
#     else:
#         mask = thresh

#     # Fit line on text pixels
#     ys, xs = np.where(mask > 0)
#     pts = np.column_stack((xs, ys)).astype(np.float32).reshape(-1, 1, 2)
#     vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01).flatten()

#     angle = math.degrees(math.atan2(vy, vx))

#     # 🔑 Normalize to [-45, 45]
#     if angle > 90:
#         angle -= 180
#     elif angle < -90:
#         angle += 180
#     if angle > 45:
#         angle -= 90
#     elif angle < -45:
#         angle += 90

#     # 🔑 Clamp small angles to 0
#     if abs(angle) <= tolerance:
#         angle = 0

#     print(f"Detected angle: {angle:.2f}° (tolerance ±{tolerance}°)")
#     return angle


# def rotate_image_auto(image_path, angle):
#     img = cv2.imread(image_path)
#     if img is None:
#         raise FileNotFoundError(f"Can't open {image_path}")

#     (h, w) = img.shape[:2]
#     center = (w // 2, h // 2)

#     if angle == 0:
#         print("Image already straight.")
#         return image_path

#     M = cv2.getRotationMatrix2D(center, -angle, 1.0)
#     rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
#                              borderMode=cv2.BORDER_REPLICATE)
#     out_path = "processed_images/straight_image.png"
#     cv2.imwrite(out_path, rotated)
#     return out_path
