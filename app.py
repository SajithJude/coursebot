import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext

import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("API_KEY")
st.subheader("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]


cola, colb ,colc= st.columns([5,5,5],gap="small")

if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = cola.selectbox("Select an index file to load:", index_filenames,label_visibility="collapsed")
    index_path = os.path.join(DATA_DIR, index_file)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=512))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.load_from_disk(index_path,service_context=service_context)
else:
    # If there are no index files available, prompt the user to upload a PDF file
    st.warning("No index files found. Please upload a PDF file to create an index.")
    

toc = colb.button("Load Chapter")
try:
    if toc:
        toc_res = index.query(f"Generate a full table of contents for this book in a json format ")
        str_toc = str(toc_res)
        print(str_toc)
        json_output = json.loads(str_toc)
        table_of_contents = json_output["Table of Contents"]
        if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents

    st.write("")
    # st.write()
    col1, col2, col3 = st.columns([3,5,5])

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []

    quer = colc.button("Extract Selected")
    # download = col3.button("Download XML")
    # col3.write("")

    for item in st.session_state.table_of_contents:
        for title, content in item.items():
            if col1.checkbox(title):
                if title not in st.session_state.selected_items:
                    st.session_state.selected_items.append(title)

    if quer:
        chapter_contents = {}
        for title in st.session_state.selected_items:
            chapter_content = index.query(f"Extract the contents under the title {title}")
            chapter_contents[title] = chapter_content.response

        if chapter_contents:
            # sav = col2.button("Save Edits")
            st.session_state.selected_chapters = chapter_contents
            
            # with col2.expander("Edit PDF Content"):
                
        for title, content in st.session_state.selected_chapters.items():
            col2.write(f"Title: {title}")
            content_key = f"{title}_content"
            if content_key not in st.session_state:
                st.session_state[content_key] = content
            content_value = col2.text_area(label="Content", value=st.session_state[content_key], key=content_key)
            
        root = ET.Element("topics")
        for key, value in st.session_state.selected_chapters.items():
            if key == "1.1 Objectives":
                topic_name = "objectives"
                topic_content = "objectives_content"
            else:
                topic_name = "topic_name"
                topic_content = "topic_content"
                
            topic = ET.SubElement(root, topic_name)
            topic.text = key
            contents = ET.SubElement(root, topic_content)
            contents.text = value

        # if col2.button("Save XML"):
            xml_string = ET.tostring(root)
            # Use minidom to pretty print the XML string
            pretty_xml = minidom.parseString(xml_string).toprettyxml()
    
        with st.expander("XML content"):
            col3.write(pretty_xml)
        
except AttributeError:
    st.warning("Click on load chapter first and select the required Topics to extract")