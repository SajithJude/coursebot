import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext

import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from llama_index import download_loader
from xml.etree.ElementTree import Element, SubElement, tostring

from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("API_KEY")
st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()


def json_to_xml(json_data):
    topics = Element('Topics')

    for topic_name, topic_info in json_data.items():
        topic = SubElement(topics, 'Topic')
        topic_name_element = SubElement(topic, 'TopicName')
        topic_name_element.text = topic_name

        subtopics = SubElement(topic, 'SubTopics')
        for subtopic_info in topic_info['Subtopics']:
            subtopic = SubElement(subtopics, 'SubTopic')

            subtopic_name = SubElement(subtopic, 'SubTopicName')
            subtopic_name.text = subtopic_info['Subtopic']

            subtopic_content = SubElement(subtopic, 'SubTopicContent')
            subtopic_content.text = subtopic_info['content']

    return tostring(topics).decode()



def save_uploaded_file(uploaded_file):
    with open(os.path.join(DATA_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

upload_col, extract_col, edit_col, xml_col = st.tabs(["⚪ __Upload Chapter__  ","⚪ __Extract_Contents__  ", "⚪ __Edit Contents__  "," ⚪ __Export Generated XML__  "])

uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")

if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
        st.success("It would take a while to index the books, please wait..!")

        pdf_filename = uploaded_file.name

        documents = loader.load_data(file=Path(f"data/{pdf_filename}"))

        index = GPTSimpleVectorIndex.from_documents(documents)

        index.save_to_disk(os.path.join(DATA_DIR, os.path.splitext(pdf_filename)[0] + ".json"))
        st.success("Index created successfully!")

if index_filenames:
    index_file = upload_col.selectbox("Select an index file to load:", index_filenames,label_visibility="collapsed")
    index_path = os.path.join(DATA_DIR, index_file)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1024))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.load_from_disk(index_path,service_context=service_context)
else:
    st.warning("No index files found. Please upload a PDF file to create an index.")

toc = upload_col.button("Genererate TOC")
try:
    if toc:
        toc_res = index.query(f"Generate a table of contents for this document with topics and subtopics in JSON format, the hierarchy of the table of contents should only have 2 levels which is topics and subtopics, dont include the topics named Objective ,Keywords,and Check Your Progress within the table of contents")
        str_toc = str(toc_res)
        table_of_contents = json.loads(str_toc)

        if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents
        upload_col.write(st.session_state.table_of_contents)

        upload_col.success("TOC loaded, Go to the next tab")

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    edit_col.warning("Select the Neccessary topics and go the next page")

    quer = extract_col.button("Extract Selected")


    new_dict = {}
    for topic in st.session_state.table_of_contents['Topics']:
        for key, value in topic.items():
            # Add a description for the topic
            new_dict[key] = {'content': '', 'Subtopics': []}
            # Add descriptions for the values
            for item in value:
                new_dict[key]['Subtopics'].append({'content': '', 'Subtopic': item})


    # edit_col.write(new_dict)

    if quer:
        for topic, subtopics_dict in new_dict.items():
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = index.query("extract the information about "+str(subtopic_name))
                st.info(f"extracting {subtopic_name}")
                subtopic_dict['content'] = subtopicres.response
            
            topicres = index.query("extract the information about "+str(topic))
            st.info(f"extracting {topic}")

            subtopics_dict['content'] = topicres.response

            updated_json = json.dumps(new_dict, indent=2)
        
        extract_col.write(new_dict)

        if "new_dict" not in st.session_state:
            st.session_state.new_dict = new_dict
            
        for topic, subtopics_dict in st.session_state.new_dict.items():
            content = subtopics_dict['content']
            subtopics_dict['content'] = edit_col.text_area(f"Topic {topic}:", value=content)
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                content = subtopic_dict['content']
                subtopic_dict['content'] = edit_col.text_area(f"Subtopic {subtopic_name} under topic {topic} :", value=content)

    if edit_col.button("Save"):
        edit_col.write(st.session_state.new_dict)

    # json_data = json.loads(st.session_state.new_dict)
    xml_output = json_to_xml(st.session_state.new_dict)

    # xml_string = ET.tostring(root)
    # pretty_xml = minidom.parseString(xml_string).toprettyxml()

    with st.expander("XML content"):
        xml_col.write(xml_output)
        
except AttributeError:
    st.warning("Click on load chapter first and select the required Topics to extract")