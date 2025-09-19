import test
import cor
import ocr_image
import consume
json_path="Raw_response/response0.json"
input_path=r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\Capture.PNG"
consume.api_consume(input_path)
test.extract_data(json_path)
ocr_image.makeimg(json_path,input_path)
cor.main(json_path)