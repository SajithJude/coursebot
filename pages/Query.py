import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext

import os
import openai 
import json

from langchain import OpenAI

openai.api_key = os.getenv("API_KEY")

DATA_DIR = "data"
# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]


if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = st.selectbox("Select an index file to load:", index_filenames)
    index_path = os.path.join(DATA_DIR, index_file)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=512))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.load_from_disk(index_path,service_context=service_context)
else:
    # If there are no index files available, prompt the user to upload a PDF file
    st.warning("No index files found. Please upload a PDF file to create an index.")
    

toc = st.button("Get TOC")

if toc:
    toc_res = index.query(f"Generate a full table of contents for this book in a json format ")
    str_toc = str(toc_res)
    # st.write(str_toc)
    json_output = json.loads(str_toc)
    table_of_contents = json_output["Table of Contents"]
    if "table_of_contents" not in st.session_state:
        st.session_state.table_of_contents = table_of_contents



try:
    selected_items = []
    for item in table_of_contents:
    for title, content in item.items():
        if st.checkbox(title):
            selected_items.append(title)
            
    if selected_items:
        st.write("Selected items:", selected_items)
except AttributeError:
    st.warning("Generate TOC to view list")  
else:
    st.warning("Click the 'Chapters' button to retrieve the table of contents.")
