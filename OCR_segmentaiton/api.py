import os
import base64
import numpy as np
from flask import Flask,request,render_template,jsonify
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from werkzeug.security import generate_password_hash,check_password_hash
import json
import uuid
from rapidfuzz import fuzz, process
import helper.straight as straight
import helper.cbox as cbox
import helper.logger as logger
import helper.text_extract as text_extract
import helper.match as match
import helper.doc_fields as doc_fields
import helper.doc_sides as doc_sides
import helper.sort_text as sort_text
import helper.pdf_extracter as pdf_extracter
import tempfile
from functools import wraps


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp','PNG'}

# Create uploads directory if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_SECRET_KEY']=os.environ.get("JWT_SECRET_KEY")
jwt=JWTManager(app)

with open("db/userinfo.json","r", encoding="utf-8") as f:
    user=json.load(f)

with open("db/enc_info.json","w",encoding="utf-8") as ef:
    hashing={"user":user["user"],"password":generate_password_hash(user["password"])}
    print(hashing)
    json.dump(hashing,ef,indent=2,ensure_ascii=False)
def require_auth(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth=request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({"msg":"Missing Username or Password"}),400
        user_password=hashing.get("password")
        if not user_password or not check_password_hash(user_password,auth.password):
            return jsonify({"msg":"Bad username and password"}),401
        return f(*args,**kwargs)
    return decorated
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

json_detected_file = 'detected/data.json'
if not os.path.isfile(json_detected_file):
    with open(json_detected_file, 'w') as f:
        json.dump([], f)

json_undetected_file='undetected/data.json'
if not os.path.isfile(json_undetected_file):
    with open(json_undetected_file, 'w') as f:
        json.dump([], f)

def binarytobase64(filepath):
    with open(filepath, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
    return encoded_string

def textcorrector(text_blocks,mathcing_text):
    for i,val in enumerate(text_blocks):
        mathces=process.extract(val,mathcing_text,scorer=fuzz.token_set_ratio)
        for word,score,index in mathces:
            if score>=60:
                text_blocks[i]=word
    return text_blocks

def data(path,output_img="output.png"):
    txn_file_name=f"TXN_{str(uuid.uuid4())[:4]}"
    t_id=txn_file_name
    angle=straight.compute_skew_projection(path)
    img_path=straight.rotate_image_auto(path,angle)
    text_input=text_extract.text_extraction(img_path)
    text_box=text_input[0]["rec_polys"]
    text_boxes=np.array(text_input[0]["rec_polys"]).tolist()
    if angle and img_path and text_input and text_boxes:
        remark="Success"
    else:
        remark="failed"
    cbox.paddle_bboxes(img_path,text_input[0]["rec_texts"],text_box,output_img)
    document_type=match.detect_document_type(text_input[0]["rec_texts"])
    print(document_type)
    if document_type=="aadhaar":
        document_sides=doc_sides.detect_document_sides(text_input[0]["rec_texts"],document_type)
        aadhaar_front_data=doc_fields.extract_adhaar_text(document_sides["front"])
        #aadhaar_back_data=extract_adhaar_text(document_sides["back"])
        response={"document_type":document_type,"ocr_result":[{"front":aadhaar_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="pan":
        document_sides=doc_sides.detect_document_sides(text_input[0]["rec_texts"],document_type)
        pan_front_data=doc_fields.extract_pan_fields(document_sides["front"])
        #pan_back_data=extract_pan_fields(document_sides["back"])
        response={"document_type":document_type,"ocr_result":[{"front":pan_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="dl":
        document_sides=doc_sides.detect_document_sides(text_input[0]["rec_texts"],document_type)
        dl_front_data=doc_fields.extract_dl_fields(document_sides["front"])
        #dl_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"ocr_result":[{"front":dl_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="voter":
        document_sides=doc_sides.detect_document_sides(text_input[0]["rec_texts"],document_type)
        voter_front_data=doc_fields.extract_voter_fields(document_sides["front"])
        #voter_back_data=extract_dl_fields(document_sides["back"])
        response={"document_type":document_type,"ocr_result":[{"front":voter_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="bank":
        document_sides=doc_sides.detect_document_sides(text_input[0]["rec_texts"],document_type)
        bank_front_data=doc_fields.extract_bank_fields(document_sides["front"])
        #bank_back_data=extract_bank_fields(document_sides["back"])
        response={"document_type":document_type,"ocr_result":[{"front":bank_front_data,"back":document_sides["back"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
    elif document_type=="other":
        response={"document_type":"other","ocr_result":[{"raw_text":text_input[0]["rec_texts"],"boundingbox":text_boxes}]}
        try:
            with open(json_undetected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_undetected_file, 'w') as f:
            json.dump(data, f, indent=2,ensure_ascii=False)
        return response

    else:
        response={"document_type":"other","ocr_result":[{"raw":text_input[0]["rec_texts"],"boundingbox":text_boxes}],"txn_id":t_id,"remark":remark}
        try:
            with open(json_undetected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_undetected_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return response
    if document_type!="other":
        try:
            with open(json_detected_file, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", str(e))

        data.append(response)

        # Save updated list back to file
        with open(json_detected_file, 'w') as f:
            json.dump(data, f, indent=2,ensure_ascii=False)
        return response

# for i in os.listdir("docs"):
#     print(data(f"docs/{i}"))

@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/ocr",methods=["GET","POST"])
def ocrapi():
    if request.method == "POST":
        if 'images' not in request.files:
            return jsonify({"error": "No images part in the request"}), 400

        files = request.files.getlist("images")

        if not files:
            return jsonify({"error": "No selected files"}), 400

        all_results_html = ""
        for file in files:
            if file and allowed_file(file.filename):
                file_path = os.path.join('uploads', file.filename)
                file.save(file_path)

                ocr_data = data(file_path)
                html_str = "<div style='font-family: Arial; line-height: 1.6;'>"
                doc_type = ocr_data.get("document_type", "Unknown")
                html_str += f"<h2>🧾 Document Type: {doc_type.upper()}</h2><hr>"

                def format_dict_section(title, section_dict):
                    section_html = f"<h3>{title}</h3><div style='margin-left: 15px;'>"
                    if isinstance(section_dict, dict):
                        for key, value in section_dict.items():
                            key_fmt = key.replace('_', ' ').capitalize()
                            if key_fmt=="Raw blocks":
                                continue
                            if isinstance(value, list):
                                section_html += f"<strong>{key_fmt}:</strong><br>"
                                for item in value:
                                    section_html += f"&nbsp;&nbsp;- {item}<br>"
                            elif isinstance(value, dict):
                                for i in value:
                                    section_html += f"<label>{i}:</label> <span>{value[i]}</span><br>"
                            else:
                                section_html += f"<strong>{key_fmt}:</strong> {value}<br>"
                    elif isinstance(section_dict, list):
                        for item in section_dict:
                            section_html += f"{item}<br>"
                    section_html += "</div><br>"
                    return section_html

                for key, value in ocr_data.items():
                    if key == "document_type":
                        continue
                    elif key == "front":
                        html_str += format_dict_section("📄 FRONT SIDE", value)
                    elif key == "back":
                        html_str += format_dict_section("📄 BACK SIDE", value)
                    else:
                        html_str += format_dict_section(key.capitalize(), value)

                html_str += "</div><hr><br>"
                # Wrap each card
                card_html = f"""
                <div class="card mb-4 shadow">
                    <div class="card-body">
                        <h5 class="card-title">Processed File: {file.filename}</h5>
                        <img src='data:image/jpeg;base64,{binarytobase64(f"static/docs/{file.filename}")}' class="img-fluid mb-3" alt="{file.filename}">
                        {html_str}
                    </div>
                </div>
                """
                all_results_html += card_html

        return render_template("data.html", data=all_results_html)
    else:
        return jsonify({"error": "Method is GET"})
@app.route("/allocr", methods=["GET","POST"])
def allocr():

    folder="static/docs/"
    file_names=os.listdir("static/docs")
    all_results_html=""
    for i in file_names:
        file_path=folder+i
        ocr_data=data(file_path)
        html_str = "<div style='font-family: Arial; line-height: 1.6;'>"
        doc_type = ocr_data.get("document_type", "Unknown")
        html_str += f"<h2>🧾 Document Type: {doc_type.upper()}</h2><hr>"

        def format_dict_section(title, section_dict):
            section_html = f"<h3>{title}</h3><div style='margin-left: 15px;'>"
            if isinstance(section_dict, dict):
                for key, value in section_dict.items():
                    key_fmt = key.replace('_', ' ').capitalize()
                    if key_fmt=="Raw blocks":
                        continue
                    if isinstance(value, list):
                        section_html += f"<strong>{key_fmt}:</strong><br>"
                        for item in value:
                            section_html += f"&nbsp;&nbsp;- {item}<br>"
                    elif isinstance(value, dict):
                        for i in value:
                            section_html += f"<label>{i}:</label> <span>{value[i]}</span><br>"
                    else:
                        section_html += f"<strong>{key_fmt}:</strong> {value}<br>"
            elif isinstance(section_dict, list):
                for item in section_dict:
                    section_html += f"{item}<br>"
            section_html += "</div><br>"
            return section_html

        for key, value in ocr_data.items():
            if key == "document_type":
                continue
            elif key == "front":
                html_str += format_dict_section("📄 FRONT SIDE", value)
            elif key == "back":
                html_str += format_dict_section("📄 BACK SIDE", value)
            else:
                html_str += format_dict_section(key.capitalize(), value)

        html_str += "</div><hr><br>"
        # Wrap each card
        card_html = f"""
        <div class="card mb-4 shadow">
            <div class="card-body">
                <h5 class="card-title">Processed File: {i}</h5>
                <img src='data:image/jpeg;base64,{binarytobase64(f"static/docs/{i}")}' class="img-fluid mb-3" alt="{i}">
                {html_str}
            </div>
        </div>
        """
        all_results_html += card_html
    return render_template("data.html",data=all_results_html)
@app.route("/api_ocr_tayyab",methods=["GET","POST"])
@require_auth
def request_ocr():
    if request.method=="POST":
        txn_file_name=f"TXN_{str(uuid.uuid4())[:4]}"
        os.makedirs(f"data/{txn_file_name}",exist_ok=True)
        os.makedirs(f"data/{txn_file_name}/Assets",exist_ok=True)
        os.makedirs(f"data/{txn_file_name}/Errorlogs",exist_ok=True)
        os.makedirs(f"data/{txn_file_name}/Input",exist_ok=True)
        os.makedirs(f"data/{txn_file_name}/Output",exist_ok=True)
        logs=logger.setup_logger("logger_app",f"data/{txn_file_name}/Errorlogs/app.log")
        logs.info("Request ocr is running")
        request_data=request.get_json(silent=True)
        with open(f"data/{txn_file_name}/Input/input0.json","w") as f:
            json.dump(request_data,f,indent=2)
            logs.info("input0.json is created")
        base_64_img=base64.b64decode(request_data["base64_image"])
        filetype=pdf_extracter.detect_filetype(request_data["base64_image"])
        print(filetype)
        if filetype=="PDF":
            final_response=[]
            pdf_extracter.pdf_pages_to_images_base64(request_data["base64_image"],f"data/{txn_file_name}/Assets/images_from_pdf")
            logs.info("Assets Done")
            os.makedirs(f"data/{txn_file_name}/Assets/images_from_pdf",exist_ok=True)
            for i in os.listdir(f"data/{txn_file_name}/Assets/images_from_pdf"):
                logs.info(f"{i} extracted form pdf")
                response=data(f"data/{txn_file_name}/Assets/images_from_pdf/{i}",f"data/{txn_file_name}/Output/boxed_output.png")
                logs.info(f"response genrated from {i}")
                print("response is generated")
                with open(f"data/{txn_file_name}/Output/{i}_response0.json","w") as f:
                    json.dump(response,f,indent=2)
                    logs.info("Response0.json is created")
                with open(f"data/{txn_file_name}/Output/{i}_OCR_text.txt","w") as f:
                    if response["document_type"]!="other":
                        f.write("\n".join(response["ocr_result"][0]["front"]["raw_blocks"]))
                        logs.info("OCR_text Extracted (document detected)")
                    else:
                        f.write("\n".join(response["ocr_result"][0]["raw_text"]))
                        logs.info("OCR_text Extracted (document is not detected)")
                if response["document_type"]!="other":
                    sort_text.main(response['ocr_result'][0]['boundingbox'],response['ocr_result'][0]['front']['raw_blocks'],f"data/{txn_file_name}/Output/{i}_OCR_sort_text.txt")
                else:
                    sort_text.main(response['ocr_result'][0]['boundingbox'],response['ocr_result'][0]['raw_text'],f"data/{txn_file_name}/Output/{i}_OCR_sort_text.txt")
                logs.info("Extracted text is now sorted")
                response.update({"page":i})
                final_response.append(response)
            return jsonify({"response":final_response}) 
        else:
            pass
            with tempfile.NamedTemporaryFile(suffix=".png",delete=False) as temp_file:
                temp_file.write(base_64_img)
                temp_file_path=temp_file.name
            with open(f"data/{txn_file_name}/Assets/image_{txn_file_name}.png","wb") as f:
                f.write(base_64_img)
                logs.info("Assets Done")
            response=data(temp_file_path,f"data/{txn_file_name}/Output/boxed_output.png")
            with open(f"data/{txn_file_name}/Output/response0.json","w") as f:
                json.dump(response,f,indent=2)
                logs.info("Response0.json is created")
            with open(f"data/{txn_file_name}/Output/OCR_text.txt","w") as f:
                if response["document_type"]!="other":
                    f.write("\n".join(response["ocr_result"][0]["front"]["raw_blocks"]))
                    logs.info("OCR_text Extracted (document detected)")
                else:
                    f.write("\n".join(response["ocr_result"][0]["raw_text"]))
                    logs.info("OCR_text Extracted (document is not detected)")
            if response['document_type']!="other":
                sort_text.main(response['ocr_result'][0]['boundingbox'],response['ocr_result'][0]['front']['raw_blocks'],f"data/{txn_file_name}/Output/OCR_sort_text.txt")
            else:
                sort_text.main(response['ocr_result'][0]['boundingbox'],response['ocr_result'][0]['raw_text'],f"data/{txn_file_name}/Output/OCR_sort_text.txt")
            logs.info("Extracted text is now sorted")
            return jsonify({"response":response})

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)