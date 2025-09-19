def extract_data(json_path):
    if type(json_path) != str:
        print("Json Path is not string")
        return None
    import json
    # Load your OCR JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    extracted_data = []

    # Safely get pages
    pages = []
    if "results" in data and len(data["results"]) > 0:
        result0 = data["results"][0]
        if "Data" in result0 and len(result0["Data"]) > 0:
            data0 = result0["Data"]
            if "responses" in data0 and len(data0["responses"]) > 0:
                response0 = data0["responses"][0]
                if "fullTextAnnotation" in response0:
                    pages = response0["fullTextAnnotation"].get("pages", [])

    # Loop through pages and extract bounding boxes, confidence, and text
    for page in pages:
        for block in page.get("blocks", []):
            for paragraph in block.get("paragraphs", []):
                for word in paragraph.get("words", []):
                    word_text = "".join([s.get("text", "") for s in word.get("symbols", [])])
                    word_confidence = word.get("confidence", None)
                    word_bbox = word.get("boundingBox", {}).get("vertices", [])

                    symbols_info = []
                    for s in word.get("symbols", []):
                        symbols_info.append({
                            "text": s.get("text", ""),
                            "confidence": s.get("confidence", None),
                            "bounding_box": s.get("boundingBox", {}).get("vertices", [])
                        })

                    extracted_data.append({
                        "word_text": word_text,
                        "confidence": word_confidence,
                        "bounding_box": word_bbox,
                        "symbols": symbols_info
                    })

    # Print results
    output=[]
    for item in extracted_data:
        output.append(json.dumps(item, ensure_ascii=False, indent=2))
    with open("output.json", "w", encoding="utf-8") as out_file:
        json.dump(extracted_data, out_file, ensure_ascii=False, indent=2)

    import json

    # Load OCR JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Function to safely extract pages
    def get_pages(data):
        if "results" in data and data["results"]:
            result0 = data["results"][0]
            if "Data" in result0 and result0["Data"]:
                data0 = result0["Data"]
                if "responses" in data0 and data0["responses"]:
                    response0 = data0["responses"][0]
                    if "fullTextAnnotation" in response0:
                        return response0["fullTextAnnotation"].get("pages", [])
        return []

    pages = get_pages(data)

    # Collect text with proper spacing/line breaks
    output_text = ""
    para=[]
    for page in pages:
        for block in page.get("blocks", []):
            for paragraph in block.get("paragraphs", []):
                para.append(paragraph)
                for word in paragraph.get("words", []):
                    for symbol in word.get("symbols", []):
                        output_text += symbol.get("text", "")
                        # Check for detected breaks
                        prop = symbol.get("property", {})
                        if "detectedBreak" in prop:
                            br_type = prop["detectedBreak"].get("type", "")
                            if br_type == "SPACE":
                                output_text += " "
                            elif br_type == "LINE_BREAK":
                                output_text += "\n"
                            elif br_type == "EOL_SURE_SPACE":  # sometimes appears in OCR JSON
                                output_text += "\n"
    print("output :",output_text)
    # Save output text to file
    with open("OCR_text/extracted_text.txt", "w", encoding="utf-8") as out_file:
        out_file.write(output_text)
    with open ("paragraphs/paragraphs.json","w", encoding="utf-8") as f:
            json.dump(para,f,indent=2,ensure_ascii=False)
    print("Extracted text saved to extracted_text.txt")

if __name__=="__main__":
    extract_data()
    print("test ran")
