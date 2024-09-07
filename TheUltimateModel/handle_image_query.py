#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import torch
import open_clip
from PIL import Image
from torchvision import transforms
import numpy as np
import pickle
import matplotlib.pyplot as plt

model  , _ , preprocess = open_clip.create_model_and_transforms("ViT-L-14-336", pretrained="openai")
tokenizer = open_clip.get_tokenizer('ViT-L-14-336')
model.eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

image_folder = ".\output\images"
image_embeddings_path = ".\model_embeddings\image_embeddings.pkl"
text_embeddings_path = ".\model_embeddings\embeddings.pkl"




def load_embeddings(embeddings_path):
    with open(embeddings_path, 'rb') as f:
        embeddings = pickle.load(f)
    return embeddings


image_embeddings = load_embeddings(image_embeddings_path)
text_embeddings = load_embeddings(text_embeddings_path)

# Now `image_embeddings` contains the loaded embeddings
def retrieve_text_by_image(query_image_path, image_embeddings, text_embeddings, model, transform, device, top_n=1):
    # Load and preprocess the query image
    query_image = Image.open(query_image_path).convert("RGB")
    query_image_tensor = transform(query_image).unsqueeze(0).to(device)
    
    # Compute the embedding of the query image
    with torch.no_grad():
        query_embedding = model.encode_image(query_image_tensor)
        query_embedding /= query_embedding.norm(dim=-1, keepdim=True)
        query_embedding = query_embedding.cpu().numpy().flatten()
    
    # Calculate similarity between the image embedding and all text embeddings
    similarities = {}
    for text_id, text_embedding in text_embeddings.items():
        similarities[text_id] = cosine_similarity([query_embedding], [text_embedding])[0][0]
    
    # Sort and return the most relevant text
    sorted_texts = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_texts[:top_n]


transform = preprocess
def retrieve_images_by_text(query_text, image_embeddings =image_embeddings, model = model, tokenizer =tokenizer, device =device, top_n=4):
    text_tokens = tokenizer([query_text]).to(device)
    
    with torch.no_grad():
        text_embedding = model.encode_text(text_tokens)
        text_embedding /= text_embedding.norm(dim=-1, keepdim=True)
        text_embedding = text_embedding.cpu().numpy().flatten()
    
    similarities = {}
    for img_name, embedding in image_embeddings.items():
        similarities[img_name] = cosine_similarity([text_embedding], [embedding])[0][0]
    
    
    sorted_images = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Load top N images
    top_images = [Image.open(os.path.join(image_folder, sorted_images[i][0])).convert("RGB") for i in range(top_n)]

    # Resize images to a common height while maintaining the aspect ratio
    resized_images = []
    common_height=256
    for img in top_images:
        # Calculate the new width while preserving the aspect ratio
        aspect_ratio = img.width / img.height
        new_width = int(common_height * aspect_ratio)
        resized_images.append(img.resize((new_width, common_height)))

    # Calculate the total width of the combined image
    total_width = sum(img.width for img in resized_images)

    # Create a new blank image with the total width and common height
    combined_image = Image.new("RGB", (total_width, common_height))

    # Paste the resized images side by side into the combined image
    x_offset = 0
    for img in resized_images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return combined_image




# In[18]:

from sklearn.metrics.pairwise import cosine_similarity

def retrieve_images_by_image(query_image_path,  image_embeddings =image_embeddings, model = model, tokenizer =tokenizer, device =device, top_n=4):
    query_image = Image.open(query_image_path).convert("RGB")
    query_image_tensor = transform(query_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        query_embedding = model.encode_image(query_image_tensor)
        query_embedding /= query_embedding.norm(dim=-1, keepdim=True)
        query_embedding = query_embedding.cpu().numpy().flatten()
    
    similarities = {}
    for img_name, embedding in image_embeddings.items():
        similarities[img_name] = cosine_similarity([query_embedding], [embedding])[0][0]
    
    sorted_images = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Load top N images
    top_images = [Image.open(os.path.join(image_folder, sorted_images[i][0])).convert("RGB") for i in range(top_n)]

    # Resize images to a common height while maintaining the aspect ratio
    resized_images = []
    common_height=256
    for img in top_images:
        # Calculate the new width while preserving the aspect ratio
        aspect_ratio = img.width / img.height
        new_width = int(common_height * aspect_ratio)
        resized_images.append(img.resize((new_width, common_height)))

    # Calculate the total width of the combined image
    total_width = sum(img.width for img in resized_images)

    # Create a new blank image with the total width and common height
    combined_image = Image.new("RGB", (total_width, common_height))

    # Paste the resized images side by side into the combined image
    x_offset = 0
    for img in resized_images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return combined_image