import json
from statistics import median

def safe_get_pages(data):
    if "results" in data and data["results"]:
        result0 = data["results"]
        if "Data" in result0 or result0[0]:
            data0 = result0[0]["Data"]
            if "responses" in data0 and data0["responses"]:
                response0 = data0["responses"][0]
                if "fullTextAnnotation" in response0:
                    return response0["fullTextAnnotation"].get("pages", [])

def extract_words(pages):
    words = []
    for page in pages:
        for block in page.get("blocks", []):
            for para in block.get("paragraphs", []):
                for w in para.get("words", []):
                    text = "".join([s.get("text", "") for s in w.get("symbols", [])])
                    bbox = w.get("boundingBox", {}).get("vertices", [])
                    if not bbox:
                        continue
                    xs = [v.get("x", 0) for v in bbox]
                    ys = [v.get("y", 0) for v in bbox]
                    x_min, x_max = min(xs), max(xs)
                    y_center = (min(ys) + max(ys)) / 2
                    height = max(ys) - min(ys)
                    words.append({
                        "text": text,
                        "x_min": x_min,
                        "y_center": y_center,
                        "height": height if height > 0 else None
                    })
    return words

def cluster_lines(words, multiplier=0.7, min_threshold=10):
    if not words:
        return []

    heights = [w["height"] for w in words if w["height"]]
    med_h = median(heights) if heights else 5
    threshold = max(med_h * multiplier, min_threshold)

    # Sort all words by y_center
    words_sorted = sorted(words, key=lambda w: w["y_center"])

    lines = []
    current_line = [words_sorted[0]]
    current_y = words_sorted[0]["y_center"]

    for w in words_sorted[1:]:
        if abs(w["y_center"] - current_y) <= threshold:
            current_line.append(w)
            # update cluster y mean
            current_y = (current_y * (len(current_line)-1) + w["y_center"]) / len(current_line)
        else:
            lines.append(current_line)
            current_line = [w]
            current_y = w["y_center"]

    if current_line:
        lines.append(current_line)

    return lines

def build_text(lines):
    out = []
    for line in lines:
        line_sorted = sorted(line, key=lambda w: w["x_min"])
        text_line = " ".join([w["text"] for w in line_sorted])
        out.append(text_line)
    return "\n".join(out)

def main(json_path):
    OUTPUT_TXT="OCR_sort_text/extracted_text.txt"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = safe_get_pages(data)
    words = extract_words(pages)

    lines = cluster_lines(words, multiplier=0.7, min_threshold=2)
    final_text = build_text(lines)

    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write(final_text)

    print("✅ Extracted text saved to", OUTPUT_TXT)
    print("---- Preview ----")
    print(final_text)

