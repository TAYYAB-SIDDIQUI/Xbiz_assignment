import test
import cor
import ocr_image
json_path="Raw_response/pan_response.json"
input_path=r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\image.png"
test.extract_data(json_path)
ocr_image.makeimg(json_path,input_path)
cor.main(json_path)