import streamlit as st
from pathlib import Path
from llama_index import download_loader
from llama_index import GPTSimpleVectorIndex, Document, LLMPredictor, ServiceContext
from tempfile import NamedTemporaryFile
import json

PDFReader = download_loader("PDFReader")

if "index" not in st.session_state:
    st.session_state.index = ""

def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))

    index = GPTSimpleVectorIndex.from_documents(documents)
    # st.session_state.index = index
    return index
        

uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Process uploaded PDF and create index
if uploaded_pdf is not None:
    # if session_state.index is None:
    st.write("Processing the PDF file and creating an index...")
    st.session_state.index = process_pdf(uploaded_pdf)
    st.write("Index created successfully!")


button = st.button("Generate TOC")
if button:
    res = st.session_state.index.query("Generate a table of contents for this document including objectives separatley, and topics with subtopics as a json object")
    json_out = json.loads(res.response)
    st.write(json_out)