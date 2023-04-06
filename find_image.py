
import os
import zipfile
from PIL import Image
import requests
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer,AutoTokenizer, CLIPImageProcessor
import pathlib
import numpy
import sys
import pinecone
import pandas as pd
import math

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")

path = pathlib.Path('./static/dataset')

def load_dataset():
  image = {}
  size = (100,100)

  image["path"] = []
  image["data"] = []

  for image_path in path.iterdir():
    image["data"].append(Image.open(str(image_path)).resize(size))
    image["path"].append(image_path)
    
    if len(image["data"]) > 99:
      break

  return pd.DataFrame(image)

def get_image_embedding(image):
  inputs = processor(images=image, return_tensors="pt", padding=True)
  embedding = model.get_image_features(**inputs).detach().numpy()
  return embedding

def dataset_embedding(dataset):
  
  dataset_embeded = dataset["data"].apply(get_image_embedding)
  return dataset_embeded

def get_text_embedding(text):

  inputs = tokenizer(text, return_tensors = "pt", padding= True)
  text_embeddings = model.get_text_features(**inputs).detach().numpy()

  return text_embeddings

def load_pinecone():
  pinecone.init(
    api_key = "ad4ad3c2-4d41-4338-a378-713925edd7e9",
    environment="us-east4-gcp"
  )

  my_index_name = "cas-etude"
  #vector_dim = data.embeddings[0].shape[1]
  
  if my_index_name not in pinecone.list_indexes():
    pinecone.create_index(name = my_index_name, 
                          dimension=512,
                          metric="cosine", shards=1,
                          pod_type='p1.x1')

  my_index = pinecone.Index(index_name = my_index_name)

  return my_index


def upload_vectors(data,my_index,a):
  data["vector_id"] = data.index+a
  data["vector_id"] = data["vector_id"].apply(str)

  final_metadata = []
  
  for index in range(len(data)):
    final_metadata.append({
        'ID':  index,
        'path': str(data.iloc[index].path)
    })

  image_IDs = data.vector_id.tolist()
  image_embeddings = [arr.tolist() for arr in data.embeddings.tolist()] 

  data_to_upsert = list(zip(image_IDs, image_embeddings, final_metadata))
  print(my_index.describe_index_stats()['total_vector_count'])
  my_index.upsert(vectors = data_to_upsert)
  print(my_index.describe_index_stats()['total_vector_count'])

def upload_dataset_on_pinecone(my_index):

  batch_size = 50
  size = (100,100)

  image = {}
  image["path"] = []
  image["data"] = []

  i = 0

  for image_path in path.iterdir():
    image["data"].append(Image.open(str(image_path)).resize(size))
    image["path"].append(image_path)

    if len(image['data']) > batch_size-1:
      print("Storing data")
      data = pd.DataFrame(image)
      data["embeddings"] = dataset_embedding(data)
      upload_vectors(data,my_index,i*batch_size)
      image["path"] = []
      image["data"] = []
      i = i+1
  if image != {}:

    print("Storing data :")
    data = pd.DataFrame(image)
    data["embeddings"] = dataset_embedding(data)
    
    upload_vectors(data,my_index)
    print("data already stored : ", i)
    image = {}
    image["path"] = []
    image["data"] = []

def main(prompt):

  my_index = load_pinecone()
  
  if my_index.describe_index_stats()['total_vector_count'] == 0:
    upload_dataset_on_pinecone(my_index)
  
  text_input = get_text_embedding(prompt).tolist()

  probs = my_index.query(text_input, top_k=4, include_metadata=True)
  
  
  for elem in probs["matches"]:
    elem['values'].append(prompt)

  return probs


#my_index = load_pinecone()
#my_index.delete(delete_all =True)