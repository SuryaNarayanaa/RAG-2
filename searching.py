#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_community.llms import Ollama



from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Initialize the BLIP model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
img_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# Paths
MODEL = "mistral"  # Use the Mistral model
model = Ollama(model=MODEL)

text_chunks_folder = 'output/chunks/'
faiss_index_path = 'model_embeddings/faiss_index.index'
vector_db_path = 'model_embeddings/embeddings.pkl'




def describe_image(image_path):
    # Load and process the image
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    # Generate description
    with torch.no_grad():
        out = img_model.generate(**inputs)
    
    # Decode the generated text
    description = processor.decode(out[0], skip_special_tokens=True)
    return description




def load_text_chunks_from_folder(folder_path):
    text_chunks = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                text_chunks.append(file.read())
    return text_chunks

def embed_text_chunks(text_chunks, model):
    return model.encode(text_chunks)

def save_embeddings(embeddings, text_chunks, path):
    with open(path, 'wb') as file:
        pickle.dump((text_chunks, embeddings), file)

def load_embeddings(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]  # Dimension of embeddings
    index = faiss.IndexFlatL2(dim)  # L2 distance index
    index.add(embeddings)  # Add embeddings to index
    return index

from transformers import AutoTokenizer, AutoModelForCausalLM




def format_output(context, question, image = None):
    """
    Use Mistral model to generate formatted output.
    """
    # Define the template
    template = """
    >>> POINTS TO REMEMBER BEFORE GENERATING THE OUTPUT
        CONSIDER YOU ARE A CHATBOT WITH NO KNOWLEDGE.
        YOU WILL GAIN KNOWLEDGE ONLY WITH THE INFORMATION/CONTEXT I GIVE YOU.
        DON'T TRY TO ANSWER OUTSIDE OF THE INFORMATION I GIVE YOU.
        GENERATE THE OUTPUTS IN A STRUCTURED MANNER.
        IF THE ANSWER TO THE QUESTION IS OUT OF THE CONTEXT, THEN RETURN THAT "THE CONTEXT IS OUT OF THE KNOWLWDGE. NO RELEVANT INFORMATION FOUND"

    >>> INFORMATION/CONTEXT : {context}
    >>> QUERY : {question}
    >>> IMAGE : {image}

    if the image is none, dont talk or hallucinate about the image, just skip the part.
    """

    # Format the template with context and question
    prompt_text = template.format(context=context, question=question ,image = image)

    # Generate a response using the Mistral model
    response = model(prompt_text)
    # Return the formatted output
    return response


# Example usage





def search_faiss(query, index, model, k=5):
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), k)  # Search for top-k similar embeddings
    return I[0]  # Returns the indices of the most similar chunks

def retrieve_and_format_results(query, index, text_chunks, model , image = None):
    if image:
        query =query + "IMAGE QUERY : \n PROMPT : Just explain about the image, dont add anything to it. \n IMAGE : "+  describe_image(image)
    indices = search_faiss(query, index, model)
    
    # Handle case where no indices are returned
    if not indices.size:
        return "No relevant information found."

    # Check for valid indices
    valid_indices = [i for i in indices if 0 <= i < len(text_chunks)]
    results = " ".join([text_chunks[i] for i in valid_indices])  # Concatenate retrieved chunks
    
    formatted_results = format_output(results ,query, image = image)
    return formatted_results

# Initialize models
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Load or create embeddings and FAISS index
if os.path.exists(vector_db_path):
    text_chunks, embeddings = load_embeddings(vector_db_path)
else:
    text_chunks = load_text_chunks_from_folder(text_chunks_folder)
    embeddings = embed_text_chunks(text_chunks, embedding_model)
    save_embeddings(embeddings, text_chunks, vector_db_path)

faiss_index = build_faiss_index(embeddings)

# Example usage


# In[2]:


# query = "what are DNA made up of, explain in detail with help of flowchart" 
def return_formated_text(question, image = None):

    
    formatted_results = retrieve_and_format_results(question, faiss_index, text_chunks, embedding_model, image)
    return formatted_results
# print("RAG :(\n")
# print(formatted_results)


# In[ ]:




