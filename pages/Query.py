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
    


toc = st.button("Chapters")

if toc:
    toc_res = index.query(f"list down the chapters of this book as a json list")
    str_toc = str(toc_res)
    st.write(str_toc)
    json_output = json.loads(str_toc)
    if "json_output" not in st.session_state:
        st.session_state.json_output = json_output

    st.write(st.session_state.json_output)


##########################################

chapter = st.text_input("chapter number")
lo = st.button("Learning Objectives")

if lo:
    lores = index.query(f"list down the learning objectives of the chapter {chapter} of this book as a json list")
    str_lo = str(lores)
    st.write(str_lo)
    json_lo = json.loads(str_lo)
    if "json_lo" not in st.session_state:
        st.session_state.json_lo = json_lo

    st.write(st.session_state.json_lo)


########################################
topi = st.button("Topics")

if topi:
    topires = index.query(f"list down the topics under the chapter {chapter} of this book as a json list")
    str_topi = str(topires)
    st.write(str_topi)
    json_topi = json.loads(str_topi)
    if "json_topi" not in st.session_state:
        st.session_state.json_topi = json_topi

    st.write(st.session_state.json_topi)

else:
    st.warning("Click the 'Table of contents' button to retrieve the table of contents.")


with st.expander("Chapters"):
    st.write(st.session_state.json_output)

with st.expander("Learning Objectives"):
    st.write(st.session_state.json_lo)

with st.expander("topics"):
    st.write(st.session_state.json_topi)

