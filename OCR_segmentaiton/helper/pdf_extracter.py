import base64
import fitz  # PyMuPDF
import os


def binarytobase64(filepath):
    with open(filepath, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
    return encoded_string

img_path=r"static\docs\Docs.pdf"
b64_string=binarytobase64(img_path)

def detect_filetype(b64_string):
    # Remove data URI prefix if present
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]

    # Decode just the first few bytes
    file_start = base64.b64decode(b64_string)[:8]

    # Check magic numbers
    if file_start.startswith(b"\xFF\xD8\xFF"):
        return "JPEG image"
    elif file_start.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG image"
    elif file_start.startswith(b"%PDF"):
        return "PDF"
    elif file_start.startswith(b"PK"):
        return "DOCX (or another ZIP-based file like XLSX, PPTX)"
    else:
        return "Unknown file type"


def pdf_pages_to_images_base64(b64_string, output_dir="pdf_pages_as_images", dpi=200):
    # Remove data URI prefix if present
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]

    # Decode Base64 into PDF bytes
    pdf_bytes = base64.b64decode(b64_string)

    # Load PDF directly from memory
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Create output folder
    os.makedirs(output_dir, exist_ok=True)

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Render page to image (dpi controls resolution)
        zoom = dpi / 72  # 72 is default dpi in PDFs
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        img_path = os.path.join(output_dir, f"page_{page_num+1}.png")
        pix.save(img_path)
        print(f"Saved: {img_path}")

    print(f"\n✅ Converted {len(pdf_document)} pages into images")

#pdf_pages_to_images_base64(b64_string)