import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext

import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from llama_index import download_loader



from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("API_KEY")
st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()

def save_uploaded_file(uploaded_file):
    with open(os.path.join(DATA_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())

# Get a list of available index files in the data directory
index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

upload_col, extract_col, edit_col, xml_col = st.tabs(["⚪ __Upload Chapter__  ","⚪ __Extract_Contents__  ", "⚪ __Edit Contents__  "," ⚪ __Export Generated XML__  "])


uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")

# cola, colb = st.columns([6,1],gap="small")
if uploaded_file is not None:
        # Save the uploaded file to the data directory
        save_uploaded_file(uploaded_file)
        st.success("It would take a while to index the books, please wait..!")
    
    # Create a button to create the index
    # if st.button("Create Index"):
        # Get the filename of the uploaded PDF
        pdf_filename = uploaded_file.name
        
        # Load the documents from the data directory
        documents = loader.load_data(file=Path(f"data/{pdf_filename}"))
        
        # Create the index from the documents
        index = GPTSimpleVectorIndex.from_documents(documents)
        
        # Save the index to the data directory with the same name as the PDF
        index.save_to_disk(os.path.join(DATA_DIR, os.path.splitext(pdf_filename)[0] + ".json"))
        st.success("Index created successfully!")




if index_filenames:
    # If there are index files available, create a dropdown to select the index file to load
    index_file = upload_col.selectbox("Select an index file to load:", index_filenames,label_visibility="collapsed")
    index_path = os.path.join(DATA_DIR, index_file)
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1024))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.load_from_disk(index_path,service_context=service_context)
else:
    # If there are no index files available, prompt the user to upload a PDF file
    st.warning("No index files found. Please upload a PDF file to create an index.")
    

toc = upload_col.button("Genererate TOC")
try:
    if toc:
        toc_res = index.query(f"Generate a table of contents for this document with topics and subtopics in JSON format, the hierarchy of the table of contents should only have 2 levels which is topics and subtopics, dont include the topics named Objective ,Keywords,and Check Your Progress within the table of contents")
        str_toc = str(toc_res)
        table_of_contents = json.loads(str_toc)
        upload_col.write(table_of_contents)

        # table_of_contents = [{"title": title} for title in toc_res]
        if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents
        upload_col.success("TOC loaded, Go to the next tab")
        

    st.write("")
    # st.write()

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    edit_col.warning("Select the Neccessary topics and go the next page")
    # edit_col.write(st.session_state.table_of_contents)
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
        # chapter_contents = {}
        for topic, subtopics_dict in new_dict.items():
    # Loop through each subtopic for the topic
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = index.query("extract the information about "+str(subtopic_name))
                # Query the value of "Topics" and "Subtopics" for the subtopic
                # and insert the response into the relevant "content" field
                subtopic_dict['content'] = subtopicres.response
            
            # Query the value of "Topics" for the topic
            # and insert the response into the relevant "content" field
            subtopics_list = [subtopic_dict['Subtopic'] for subtopic_dict in subtopics_dict['Subtopics']]
            topicres = index.query("extract the information about "+str(topic))
            # topics_content = f"Content for {topic} topic. Subtopics: {', '.join(subtopics_list)}"
            subtopics_dict['content'] = topicres.response

            # Convert the updated dictionary to JSON
            updated_json = json.dumps(new_dict, indent=2)
        
        extract_col.write(new_dict)

        if "new_dict" not in st.session_state:
            st.session_state.new_dict = new_dict
            
            # with extract_col.expander("Edit PDF Content"):
                
        # Loop through each topic in the JSON dictionary
        for topic, subtopics_dict in st.session_state.new_dict.items():
            # Get the content for the topic
            content = subtopics_dict['content']
            # Create a text input field for the content and store the updated content in the dictionary
            subtopics_dict['content'] = edit_col.text_area(f"Topic {topic}:", value=content)
            # Loop through each subtopic for the topic
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                # Get the content for the subtopic
                content = subtopic_dict['content']
                # Create a text input field for the content and edit_colore the updated content in the dictionary
                subtopic_dict['content'] = edit_col.text_area(f"Subtopic {subtopic_name} under topic {topic} :", value=content)

        # Create a "Save" button
        if edit_col.button("Save"):
            # Convert the updated dictionary to JSON
            # updated_json = json.dumps(st.session_state.new_dict, indent=2)
            # Write the updated JSON to a file or database, or print it to the console
            edit_col.write(st.session_state.new_dict)



        root = ET.Element("chapter")
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

        # if extract_col.button("Save XML"):
            xml_string = ET.tostring(root)
            # Use minidom to pretty print the XML string
            pretty_xml = minidom.parseString(xml_string).toprettyxml()
    
        with st.expander("XML content"):
            xml_col.write(pretty_xml)
        
except AttributeError:
    st.warning("Click on load chapter first and select the required Topics to extract")