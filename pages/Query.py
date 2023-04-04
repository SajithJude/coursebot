import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt
import os
import openai 
import json


openai.api_key = os.getenv("API_KEY")

DATA_DIR = "data"
# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]


if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = st.selectbox("Select an index file to load:", index_filenames)
    index_path = os.path.join(DATA_DIR, index_file)
    index = GPTSimpleVectorIndex.load_from_disk(index_path)
else:
    # If there are no index files available, prompt the user to upload a PDF file
    st.warning("No index files found. Please upload a PDF file to create an index.")
    
chapter = st.text_input("chapter number")
toc = st.button("Table of contents")

if toc:
    toc_res = index.query(f"list down the topics in the {chapter} of this book as a json list")
    str_toc = str(toc_res)
    st.write(str_toc)
    json_output = json.loads(str_toc)
    st.write(json_output)

    if toc_res:
        toc_list = [item.text for item in toc_res]
        selected_toc = st.radio("Select a table of contents item:", toc_list)
    else:
        st.warning("No table of contents found.")
else:
    st.warning("Click the 'Table of contents' button to retrieve the table of contents.")
