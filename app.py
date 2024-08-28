from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_cors import CORS  # Import CORS
import os
import logging

from TheUltimateModel.pdf_scanners import extract_data_from_directory
from TheUltimateModel.chunking import generate_chunks
from TheUltimateModel.saveing_model_params import saving_the_model
from TheUltimateModel.querying_from_the_model import retrieve_and_format_results, build_faiss_index, load_embeddings
from searching import return_formated_text
app = Flask(__name__)
CORS(app)

# Global variables
EMBEDDING_PKL, EMBEDDING_INDEX = None, None

@app.route('/', methods=['POST'])
def handle_question():
    data = request.get_json()
    question = data.get('question', '')

    response_text = return_formated_text(question)
    return jsonify({'response': response_text})

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)

        EXTRACTED_TEXT_FILE = extract_data_from_directory(UPLOAD_FOLDER)
        CHUNK_PATH = generate_chunks(EXTRACTED_TEXT_FILE)

        global EMBEDDING_PKL, EMBEDDING_INDEX
        EMBEDDING_PKL, EMBEDDING_INDEX = saving_the_model(CHUNK_PATH, EXTRACTED_TEXT_FILE)
        
        return jsonify({'response': "FILE UPLOADED AND MODEL SAVED SUCCESSFULLY", 'embedding_pkl': EMBEDDING_PKL, 'embedding_index': EMBEDDING_INDEX})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload/chat', methods=['POST'])
def handle_chat():
    global EMBEDDING_PKL, EMBEDDING_INDEX
    print("IN HANDLE CHAT : \n" , EMBEDDING_PKL, EMBEDDING_INDEX)

    if EMBEDDING_PKL is None:
        return jsonify({'error': 'No pkl provided'}), 400

    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    text_chunks, embeddings = load_embeddings(EMBEDDING_PKL)
    faiss_index = build_faiss_index(embeddings)

    response_text = retrieve_and_format_results(question, faiss_index, text_chunks)
    return jsonify({'response': response_text})

if __name__ == '__main__':
    logging.info("Starting the Flask app...")
    if not os.path.exists(UPLOAD_FOLDER):
        logging.info("Creating upload folder...")
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
