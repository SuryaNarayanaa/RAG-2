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

# Initialize model and tokenizer
model  , _ , preprocess = open_clip.create_model_and_transforms("ViT-L-14-336", pretrained="openai")
tokenizer = open_clip.get_tokenizer('ViT-L-14-336')
model.eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

image_folder = "..\output\images"
embeddings_file = "..\model_embeddings\image_embeddings.pkl"

transform = preprocess

def compute_image_embeddings(image_folder, model, transform, device):
    embeddings = {}
    for img_name in os.listdir(image_folder):
        img_path = os.path.join(image_folder, img_name)
        image = Image.open(img_path).convert("RGB")
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            feature = model.encode_image(image_tensor)
            feature /= feature.norm(dim=-1, keepdim=True) 
            embeddings[img_name] = feature.cpu().numpy().flatten()  
    return embeddings

image_embeddings = compute_image_embeddings(image_folder, model, transform, device)

with open(embeddings_file, 'wb') as f:
    pickle.dump(image_embeddings, f)

print(f"Embeddings saved to {embeddings_file}")


# In[7]:



# In[ ]:




