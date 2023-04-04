import os
import streamlit as st
import PyPDF2
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
import openai
from pathlib import Path
from llama_index import download_loader

# Define the data directory path
DATA_DIR = "data"

openai.api_key = os.getenv("API_KEY")
PDFReader = download_loader("PDFReader")
loader = PDFReader()

def save_uploaded_file(uploaded_file):
    with open(os.path.join(DATA_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def main():
    st.title("DocuBOT Admin")


    # Create a file uploader widget
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    # Check if a file was uploaded
    if uploaded_file is not None:
        # Save the uploaded file to the data directory
        save_uploaded_file(uploaded_file)
        st.success("It would take a while to index the books, please wait..!")
        # Create a button to create the index
    # if st.button("Create Index"):
        # Get the filename of the uploaded PDF
        pdf_filename = uploaded_file.name
        
        # Load the documents from the data directory
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        
        # Create the index from the documents
        index = GPTSimpleVectorIndex.from_documents(documents)
        
        # Save the index to the data directory with the same name as the PDF
        index.save_to_disk(os.path.join(DATA_DIR, os.path.splitext(pdf_filename)[0] + ".json"))
        st.success("Index created successfully!")
    