#!/usr/bin/env python
# coding: utf-8

# In[31]:


import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from semantic_chunkers import StatisticalChunker
from semantic_router.encoders import HuggingFaceEncoder



# In[59]:


CHUNK_OP_DIRECTORY_TXT = ".\\output\\chunks"



# In[60]:


embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


# In[35]:


embedding_model_chunks =HuggingFaceEncoder()
chunker= StatisticalChunker(encoder=embedding_model_chunks)


# In[52]:


def read_entire_txt_file(FILE_PATH):

    
    with open(FILE_PATH , 'r') as f:
        text = f.read()
        f.close()
    print("TEXT READ SUCCESSFUL")
    return text



# In[53]:


def chunk_and_save_as_txt(text):


    chunks= chunker([text])
    splits = [chunk.splits for sublist in chunks for chunk in sublist]

    chmks_files= os.listdir(CHUNK_OP_DIRECTORY_TXT)
    for f in chmks_files:
        f = os.path.join(CHUNK_OP_DIRECTORY_TXT ,f)
        os.remove(f)

    for i , indv_chunk in enumerate(splits):
        CHUNK_PATH = os.path.join(CHUNK_OP_DIRECTORY_TXT , f"chunk_{i+1}.txt")
        with open(CHUNK_PATH , 'w') as f:
            f.write(str(indv_chunk))
            f.close()
    print("CHUNK SAVE SUCCESSFUL")

    return CHUNK_OP_DIRECTORY_TXT
    
    
    

        



# In[54]:


def generate_chunks(path):
    text = read_entire_txt_file(path)

    chunk_path = chunk_and_save_as_txt(text)
    print("CHUNKS GENERATED SUCCESSFULLY")
    return chunk_path


# In[55]:




# In[61]:





# In[ ]:




