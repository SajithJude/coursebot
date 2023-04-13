import streamlit as st
from pathlib import Path
from llama_index import download_loader
from llama_index import GPTSimpleVectorIndex, Document, LLMPredictor, ServiceContext
from tempfile import NamedTemporaryFile
import json
from langchain import OpenAI
PDFReader = download_loader("PDFReader")
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from xml.dom import minidom


if "index" not in st.session_state:
    st.session_state.index = ""

if "json_out" not in st.session_state:
    st.session_state.json_out = ""

def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1024))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.from_documents(documents,service_context=service_context)
    # st.session_state.index = index
    return index
        
import xml.etree.ElementTree as ET

def create_element(parent, name, text):
    element = ET.SubElement(parent, name)
    element.text = text
    return element

def create_xml_from_dict(data):
    root = ET.Element("chapter")
    
    for topic, subtopics in data.items():
        topic_element = ET.SubElement(root, "Topics")
        topic_title_element = create_element(topic_element, "TopicName", topic)
        
        for subtopic, content in subtopics.items():
            subtopic_element = ET.SubElement(topic_element, "SubTopics")
            subtopic_title_element = create_element(subtopic_element, "SubTopicName", subtopic)
            subtopic_content_element = create_element(subtopic_element, "SubTopic", content)
    
    return ET.tostring(root, encoding="unicode")

# Your dictionary goes here
# topics = {
#     # ...
# }


uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Process uploaded PDF and create index
if uploaded_pdf is not None:
    # if session_state.index is None:
    st.write("Processing the PDF file and creating an index...")
    st.session_state.index = process_pdf(uploaded_pdf)
    st.write("Index created successfully!")

structure = """{
  "Chapter": {
    "ChapterName": "",
    "Topics": {
      "Topic": [
        {
          "TopicName": "",
          "SubTopics": {
            "SubTopic": [
              {
                "SubTopicName": "",
                "SubTopicContent": ""
              },
              {
                "SubTopicName": "",
                "SubTopicContent": ""
              }
            ]
          }
        },
        {
          "TopicName": "",
          "SubTopics": {
            "SubTopic": [
              {
                "SubTopicName": "",
                "SubTopicContent": ""
              },
              {
                "SubTopicName": "",
                "SubTopicContent": ""
              }
            ]
          }
        }
      ]
    }
  }
}
"""
button = st.button("Generate TOC")
if button:
    res = st.session_state.index.query("Generate a table of contents for this document in a json format ")
    json_out = json.loads(res.response)
    st.session_state.json_out = json_out
    st.write(json_out)

try:

    for section, subsections in st.session_state.json_out.items():
        for subsection, value in subsections.items():
            response = st.session_state.index.query("Extract the information about :"+ str(subsection))
            st.session_state.json_out[section][subsection] = response.response

    st.write(st.session_state.json_out)


    xml_string = create_xml_from_dict(st.session_state.json_out)
    pretty_xml = minidom.parseString(xml_string).toprettyxml()
    st.code(pretty_xml)

except AttributeError:
    st.info("Upload Book and Generate TOC")



# objectives = st.button("Generate Objectives")
# if button:
#     out = st.session_state.index.query("Extract the list of Objectives of this documents as a Json list")
#     json_objective = json.loads(out.response)
#     st.write(json_objective)