from paddleocr import PaddleOCR
import numpy as np
import cv2


# img_path=r"static\docs\dhapubal.png"
# angle=straight.compute_text_angle_for_best_word(img_path,draw_result=False)
# print(angle)
# path=straight.rotate_image_auto(img_path,angle)

# ocr=PaddleOCR(use_angle_cls=True)
# results=ocr.ocr(path)

def paddle_bboxes(path,texts,boxes,output_img):
    img=cv2.imread(path)

    for bbox,text in zip(boxes,texts):
        pts = [(int(x), int(y)) for x, y in bbox]
        cv2.polylines(img,[np.array(pts,dtype=np.int64)],isClosed=True,thickness=2,color=(255,0,0))
        x,y=pts[0]
        cv2.putText(img, text, (x, y - 2), cv2.FONT_HERSHEY_SIMPLEX,
                        0.2, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.imwrite(output_img,img)
        