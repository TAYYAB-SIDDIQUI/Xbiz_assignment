import test
import cor
import ocr_image
import consume
import straight
import matplotlib.pyplot as plt

json_path="Raw_response/response0.json"
input_path=r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\dhapubal.png"
angle=straight.compute_text_angle_for_best_word(input_path,draw_result=False)
print("The angle is : ",angle)
path=straight.rotate_image_auto(input_path,angle)
consume.api_consume(path)
test.extract_data(json_path)
ocr_image.makeimg(json_path,path)
cor.main(json_path)