import streamlit as st
from llama_index import (
    GPTVectorStoreIndex, Document, SimpleDirectoryReader,
    QuestionAnswerPrompt, LLMPredictor, ServiceContext
)
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile
import base64
import io
from PIL import Image
import ast
import os
import glob
import openai
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import requests
import zipfile
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine


openai.api_key = os.getenv("OPENAI_API_KEY")
PDFReader = download_loader("PDFReader")

loader = PDFReader()


def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=3900))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    
    if "index" not in st.session_state:
        index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
        retriever = index.as_retriever(retriever_mode='embedding')
        index = RetrieverQueryEngine(retriever)
        st.session_state.index = index
    # st.session_state.index = index
    return st.session_state.index


cs_format = """
{
  "CourseStructure": {
    "Scenes": [
      {
        "Scene1": {
          "Title": "description or URL of image",
          "TextOverlay": "description or text to be shown",
          "Voiceover": "description or script of voiceover"
        },
        "Scene2": {
          "Title": "description or URL of image",
          "TextOverlay": "description or text to be shown",
          "Voiceover": "description or script of voiceover"
        },
        "Scene3": {
          "Title": "description or URL of image",
          "TextOverlay": "description or text to be shown",
          "Voiceover": "description or script of voiceover"
        }
        // Add more scenes as needed
      }
    ]
  }
}
"""
def call_openai(source):
    messages=[{"role": "system", "content": source}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages
       
    )
    return response.choices[0].message.content





uploaded_file = st.file_uploader("Upload a Chapter as a PDF file", type="pdf")

if uploaded_file is not None:
        # clear_all_json_files()

        # index = 
        if "index" not in st.session_state:
            st.session_state.index = process_pdf(uploaded_file)

        st.success("Index created successfully")


if "index" in st.session_state:

  vid_duration = st.slider("How long is the video ?")
  if "vid_duration" not in st.session_state:
    st.session_state.vid_duration = vid_duration

  video_type = st.radio("Type of Video", ["casestudy", "elearning", "custom"])
  if video_type == "custom":
    video_type = st.text_input("What kind of video content would you like to make ?")
  if "video_type" not in st.session_state:
    st.session_state.video_type = video_type


if st.button("Get Video structure"):
  query = f"Generate an optimal video content structure with scenes and titles for a {st.session_state.video_type} video of duration {st.session_state.vid_duration} minutes fron this document"
  course_structure = st.session_state.index.query(query).response
  if "course_structure" not in st.session_state:
    st.session_state.course_structure = course_structure

try:

  if st.session_state.course_structure is not None:
    modify_cs = st.text_area("Modify the structure if needed", value=st.session_state.course_structure)
    if st.button("Confirm Structure"):
      convert_prompt = "Convert the following content structure into a json string, use the JSON format given bellow:\n"+ "Content Structure:\n"+ modify_cs.strip() + "\n JSON format:\n"+ str(cs_format) + ". Output should be a valid JSON string."
      json_cs = call_openai(convert_prompt)
      st.write(json_cs)
      cs_dictionary = json.loads(json_cs.strip())
      if "cs_dictionary" not in st.session_state:
        st.session_state.cs_dictionary = cs_dictionary
      st.write(st.session_state.cs_dictionary)

except:
  print("Upload a document to get started")


if st.button("Get data"):
  for scene in st.session_state.cs_dictionary["CourseStructure"]["Scenes"]:
    for scene_name, scene_data in scene.items():
        opening_shot = scene_data["Title"]
        overlay = st.session_state.index.query(f"Generate some short text content to display in a slide titled as {opening_shot}").response.strip()
        voiceover = st.session_state.index.query(f"Generate a voice over script to narrate in a slide Titled  {opening_shot}").response.strip()
        st.write(scene_name)
        st.info(overlay)
        st.info(voiceover)

        scene_data["TextOverlay"] = overlay
        scene_data["Voiceover"] = voiceover
  st.write(st.session_state.cs_dictionary)



api_token = st.text_input('Enter your Synthesia API token')
template_id = st.text_input('Enter your Synthesia template ID')


try:
    
  for scene in st.session_state.cs_dictionary["CourseStructure"]["Scenes"]:
      for scene_name, scene_data in scene.items():
          # Display scene data
          with st.expander(scene_name):
              st.write(f"Opening Shot: {scene_data['Title']}")
              st.write(f"Text Overlay: {scene_data['TextOverlay']}")
              st.write(f"Voiceover: {scene_data['Voiceover']}")

          # Button to start scene video creation process
          if st.button(f'Create {scene_name} Video'):
              st.write(f'Starting {scene_name} video creation process...')

              # Define the headers for the API request
              headers = {
                  'Authorization': api_token,
                  'Content-Type': 'application/json'
              }

              # Define the data for the API request
              api_data = {
                  "title": scene_name,
                  "description": scene_data['TextOverlay'],
                  "visibility": "public",
                  "templateId": template_id,
                  "templateData": {
                      "script": scene_data['Voiceover'],
                      "Scene_Name": scene_name,
                      "Text_Overlay": scene_data['TextOverlay'],
                  },
                  "test": True,
                  "callbackId": "john@example.com"
              }

              # Make the API request
              response = requests.post('https://api.synthesia.io/v2/videos/fromTemplate', headers=headers, data=json.dumps(api_data))

              # Handle the response
              if response.status_code == 200:
                  st.write(f'{scene_name} video creation process started successfully.')
                  video_id = response.json()['id']
                  st.write(f'Video ID for {scene_name}: {video_id}')
              else:
                  st.write(f'An error occurred during the video creation process for {scene_name}.')
                  st.write(f'Response status code: {response.status_code}')
                  st.write(f'Response content: {response.content}')
except:
  st.info("Get data before creating the video")