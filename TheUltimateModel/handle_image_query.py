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

image_folder = "..\output\images"
embeddings_file = "..\model_embeddings\image_embeddings.pkl"

transform = preprocess


def show_images(image_folder, top_images):
    plt.figure(figsize=(15, 5))
    for i, (img_name, similarity) in enumerate(top_images):
        img_path = os.path.join(image_folder, img_name)
        image = Image.open(img_path)
        
        plt.subplot(1, len(top_images), i + 1)
        plt.imshow(image)
        plt.title(f"Similarity: {similarity:.2f}")
        plt.axis('off')
    
    plt.show()

# Example usage


# In[17]:


from sklearn.metrics.pairwise import cosine_similarity

def retrieve_images_by_image(query_image_path, image_embeddings, model, transform, device, top_n=1):
    # Preprocess and compute embedding for the query image
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
    return sorted_images[:top_n]




# In[18]:


def retrieve_images_by_text(query_text, image_embeddings, model, tokenizer, device, top_n=2):
    
    text_tokens = tokenizer([query_text]).to(device)
    
    with torch.no_grad():
        text_embedding = model.encode_text(text_tokens)
        text_embedding /= text_embedding.norm(dim=-1, keepdim=True)
        text_embedding = text_embedding.cpu().numpy().flatten()
    
    similarities = {}
    for img_name, embedding in image_embeddings.items():
        similarities[img_name] = cosine_similarity([text_embedding], [embedding])[0][0]
    
    sorted_images = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    return sorted_images[:top_n]


