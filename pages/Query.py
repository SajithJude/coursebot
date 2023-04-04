import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext

import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


from langchain import OpenAI

openai.api_key = os.getenv("API_KEY")

DATA_DIR = "data"
# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]


if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = st.selectbox("Select an index file to load:", index_filenames)
    index_path = os.path.join(DATA_DIR, index_file)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1024))
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

col1, col2 = st.columns(2)

if "selected_items" not in st.session_state:
    st.session_state.selected_items = []

for item in st.session_state.table_of_contents:
    for title, content in item.items():
        if col1.checkbox(title):
            if title not in st.session_state.selected_items:
                st.session_state.selected_items.append(title)

if st.button("Query"):
    chapter_contents = {}
    for title in st.session_state.selected_items:
        chapter_content = index.query(f"Extract the contents under the title {title}")
        chapter_contents[title] = chapter_content.response

    if chapter_contents:
        st.session_state.selected_chapters = chapter_contents
        root = ET.Element("topics")
        for key, value in st.session_state.selected_chapters.items():
            topic = ET.SubElement(root, "topic_name")
            topic.text = key
            contents = ET.SubElement(root, "topic_contents")
            contents.text = value
        xml_string = ET.tostring(root)
        pretty_xml = minidom.parseString(xml_string).toprettyxml()
        col2.code(pretty_xml, language=None)


# try:
#     col2.write(st.session_state.selected_chapters)
# except AttributeError:
#     pass

if not st.session_state.selected_items:
    st.warning("Please select some chapters to extract")
