def create():
    import cv2
    import numpy as np
    import json
    import matplotlib.pyplot as plt


    with open("output.json","r",encoding="utf-8") as f:
        data=json.load(f)


    path=r"E:\Xbiz_assignment\OCR_segmentaiton\static\docs\image.png"
    def makeboxes(filepath,boxpoints,texts,condidence):
    # Load your image
        img = cv2.imread(filepath)  # replace with your image path

        # Example points (x, y) of the rectangle corners
        boxes = boxpoints
        print(len(boxes))

        for box, text in zip(boxes, texts):
            points = np.array(box, dtype=np.int32).reshape((-1, 1, 2))

        # Draw the rectangle
            cv2.polylines(img, [points], isClosed=True, color=(0, 255, 0), thickness=2)

        # Choose a position for the text (top-left corner of the box)
            x, y = box[0]

        # Put text above/inside the box
            cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.4, color=(0, 0, 0), thickness=1)
        cv2.imwrite("output.jpg",img)

    boxpoints=[]
    texts=[]
    for i,val1 in enumerate(data):
        text=data[i]["word_text"]
        texts.append(text)
        points=[]
        for j,val2 in enumerate(data[i]["bounding_box"]):
            points.append([data[i]["bounding_box"][j]["x"],data[i]["bounding_box"][j]["y"]])
        boxpoints.append(points)
        condfidence=data[i]["confidence"]
    makeboxes(path,boxpoints,texts,condfidence)
