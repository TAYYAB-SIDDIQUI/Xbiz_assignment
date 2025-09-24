from helper import straight
from paddleocr import PaddleOCR
import json
from statistics import median
import numpy as np

def words_maker(boxes,texts):
    words=[]
    for bbox,text in zip(boxes,texts):
        xs = [x for x,y in bbox]
        ys = [y for x,y in bbox]
        print(xs)
        print(ys)
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

def main(boxes,texts,output):
    OUTPUT_TXT=output

    words = words_maker(boxes,texts)

    lines = cluster_lines(words, multiplier=0.7, min_threshold=2)
    final_text = build_text(lines)

    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write(final_text)

    print("✅ Extracted text saved to", OUTPUT_TXT)
    print("---- Preview ----")
    print(final_text)

