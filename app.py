from flask import Flask, render_template, request, jsonify, url_for, redirect , send_file
from flask_cors import CORS
import os
from io import BytesIO
import logging
from TheUltimateModel.pdf_scanners import extract_data_from_directory
from TheUltimateModel.chunking import generate_chunks
from TheUltimateModel.saveing_model_params import saving_the_model
from TheUltimateModel.querying_from_the_model import retrieve_and_format_results, build_faiss_index, load_embeddings
from TheUltimateModel.generate_flowchart import generate_flow_chart
from TheUltimateModel.generate_csv import create_csv
from update_embedding_path_to_DB import update_document_paths, get_document_paths

from searching import return_formated_text


from TheUltimateModel.handle_image_query import retrieve_images_by_image ,retrieve_images_by_text 

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST'])
def handle_question():
    
    
    image = request.files.get('image') if request.files.get('image') else None

    
    
    
    

    return_img =  request.form.get('return_img') if request.form.get('return_img') else None
    return_flowchart =  request.form.get('return_flowchart') 
    return_table = request.form.get("return_table")
    



    question = request.form.get('question')


    if return_img:
        if return_img == "text":
            images_queried = retrieve_images_by_text(question)
            name_of_img_path = question[:len(question)-1]
        else:
            if image: 
                
                images_queried = retrieve_images_by_image(image)
                name_of_img_path = image.filename

    


        


        # Assuming images_queried is the Image object, convert it to bytes
        image_bytes = BytesIO()
        images_queried.save(image_bytes, format="PNG")  # Save the image to a BytesIO object in PNG format
        image_bytes = image_bytes.getvalue()
        
        
        with open(f"./retrieved_imgs/{name_of_img_path}.png", "wb") as f:
            f.write(image_bytes)

        return send_file(f"./retrieved_imgs/{name_of_img_path}.png", mimetype='image/png')
    
    elif return_flowchart == 'true':
        mermaid_code = return_formated_text(question , flowchart = True)
    

        flow_chart_path  = generate_flow_chart(mermaid_code , question)

        with open(f"{flow_chart_path}.png", "rb") as f:
            image_data = f.read()

        # Use BytesIO to create an in-memory byte stream
        image_bytes = BytesIO(image_data)

        # Optionally, use PIL to manipulate the image if needed
        # image = Image.open(image_bytes)
        # Do any processing with the image if required

        # Write image back to BytesIO if needed
        # image.save(image_bytes, format="PNG")
        # image_bytes.seek(0)  # Reset the stream position to the beginning

        # Return the image using send_file
        return send_file(BytesIO(image_data), mimetype='image/png', as_attachment=False)
    

    elif return_table == 'true':
        
        csv_text = return_formated_text(question , table = True)

        csv_file_path = create_csv(csv_text ,question)
        return send_file(csv_file_path, mimetype='text/csv', as_attachment= False)

        

    if image:
            
        response_text = return_formated_text(question, image)
        return jsonify({'response': response_text})
    else:
            
        response_text = return_formated_text(question, image )
        return jsonify({'response': response_text})
        


@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    chat_id = request.form.get('chat_id')
    
    if not chat_id or file.filename == '':
        return jsonify({'error': 'No chat_id or no selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename_folder = os.path.join(UPLOAD_FOLDER, chat_id)
        os.makedirs(filename_folder, exist_ok=True)
        filename = os.path.join(filename_folder, file.filename)
        file.save(filename)

        EXTRACTED_TEXT_FILE = extract_data_from_directory(filename_folder, chat_id)
        CHUNK_PATH = generate_chunks(EXTRACTED_TEXT_FILE, chat_id)

        EMBEDDING_PKL, EMBEDDING_INDEX = saving_the_model(CHUNK_PATH, EXTRACTED_TEXT_FILE, chat_id=chat_id)
        update_document_paths(chat_id=chat_id, pdf_folder_path=filename_folder, embedding_pkl_path=EMBEDDING_PKL, embedding_index_path=EMBEDDING_INDEX)
        
        return jsonify({'response': "File uploaded and model saved successfully", 'embedding_pkl': EMBEDDING_PKL, 'embedding_index': EMBEDDING_INDEX})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload/chat', methods=['POST'])
def handle_chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    
    if not chat_id:
        return jsonify({'error': 'No chat_id provided'}), 400
    
    paths = get_document_paths(chat_id)
    
    if paths:
        EMBEDDING_PKL = paths['embedding_pkl_path']
        EMBEDDING_INDEX = paths['embedding_index_path']
        
        text_chunks, embeddings = load_embeddings(EMBEDDING_PKL)
        faiss_index = build_faiss_index(embeddings)
    else:
        return jsonify({'error': 'No document found for the given chat_id'}), 400
    
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    response_text = retrieve_and_format_results(question, faiss_index, text_chunks)
    return jsonify({'response': response_text})



if __name__ == '__main__':
    logging.info("Starting the Flask app...")
    if not os.path.exists(UPLOAD_FOLDER):
        logging.info("Creating upload folder...")
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
