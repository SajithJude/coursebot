import streamlit as st
from llama_index import GPTSimpleVectorIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile

PDFReader = download_loader("PDFReader")
import os
import openai 
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from llama_index import download_loader
from xml.etree.ElementTree import Element, SubElement, tostring
import requests


from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")
st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()

def load_db():
    if not os.path.exists("db.json"):
        with open("db.json", "w") as f:
            json.dump({}, f)
    
    with open("db.json", "r") as f:
        db = json.load(f)
    
    return db

def delete_chapter(chapter_name):
    db = load_db()
    if chapter_name in db:
        del db[chapter_name]
        with open("db.json", "w") as f:
            json.dump(db, f)
        return True
    return False

def post_xml_string(xml_string):
    url = 'https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourse'
    headers = {
        'Content-type': 'application/json'
    }
    payload = json.dumps({"ImportXML": str(xml_string)})
    response = requests.request("POST",url, headers=headers, data=payload)
    # print(data)
    print(response)
    return response


def json_to_xml(json_data, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets):
    chapter = Element('Chapter')

    no_of_bullets_element = SubElement(chapter, 'NoOfBullets')
    no_of_bullets_element.text = str(NoOfBullets)

    no_of_words_per_bullet_element = SubElement(chapter, 'NoOfWordsPerBullet')
    no_of_words_per_bullet_element.text = str(NoOfWordsPerBullet)

    no_of_words_for_vo_per_bullet_element = SubElement(chapter, 'NoOfWordsForVOPerBullet')
    no_of_words_for_vo_per_bullet_element.text = str(NoOfWordsForVOPerBullet)

    chapter_name_element = SubElement(chapter, 'ChapterName')
    chapter_name_element.text = chapter_name

    topics = SubElement(chapter, 'Topics')

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

    return tostring(chapter).decode()



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
        

index_filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

upload_col,  extract_col, edit_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__", "⚪ __Extract_Contents__", "⚪ __Edit Contents__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])

uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")

forma = """"{
  "Topics": [
    {
      "Topic 1": [
        "Subtopic 1.1",
        "Subtopic 1.2",
        "Subtopic 1.3"
      ]
    },
    {
      "Topic 2": [
        "Subtopic 2.1",
        "Subtopic 2.2",
        "Subtopic 2.3"
      ]
    },
     continue with topics...
  ]
}

"""
if uploaded_file is not None:
        index = process_pdf(uploaded_file)
        if "index" not in st.session_state:
            st.session_state.index = index

        upload_col.success("Index created successfully")


toc = upload_col.button("Genererate TOC")
try:
    if toc:
        toc_res = st.session_state.index.query(f" create a table of contents with topics and subtopics by reading through the document and create a table of contents that accurately reflects the main topics and subtopics covered in the document. The table of contents should be in the following format: " + str(forma))
        str_toc = str(toc_res)
        table_of_contents = json.loads(str_toc)

        if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents
        upload_col.write(st.session_state.table_of_contents)

        upload_col.success("TOC loaded, Go to the next tab")
    


    # if "selected_items" not in st.session_state:
    #     st.session_state.selected_items = []
    # edit_col.warning("Select the Neccessary topics and go the next page")

    quer = extract_col.button("Extract Selected")


    new_dict = {}
    for topic in st.session_state.table_of_contents["Topics"]:
        for key, value in topic.items():
            # Add a description for the topic
            new_dict[key] = {'content': '', 'Subtopics': []}
            # Add descriptions for the values
            for item in value:
                new_dict[key]['Subtopics'].append({'content': '', 'Subtopic': item})


    # edit_col.write(new_dict)

    if quer:
        progress_bar = extract_col.progress(0)
        total_items = sum(len(subtopics_dict['Subtopics']) for _, subtopics_dict in new_dict.items()) + len(new_dict)
        items_processed = 0
        for topic, subtopics_dict in new_dict.items():
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = index.query("extract the information about "+str(subtopic_name))
                subtopic_dict['content'] = subtopicres.response
                items_processed += 1
                progress_bar.progress(items_processed / total_items)
                extract_col.info(f"Extracted {subtopic_name}")
            
            topicres = index.query("extract the information about "+str(topic))
            subtopics_dict['content'] = topicres.response
            items_processed += 1
            progress_bar.progress(items_processed / total_items)


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
        pass 

    if edit_col.button("Save"):
        edit_col.write(st.session_state.new_dict)



    chapter_name = xml_col.text_input("enter chapter name")
    NoOfBullets = xml_col.text_input("No. of Bullets per Sub Topic")
    NoOfWordsPerBullet = xml_col.text_input("No. of words per Bullet")
    NoOfWordsForVOPerBullet = xml_col.text_input("No. of words for Voice Over per Bullet")

    save_xml = xml_col.button("Save XML")
    if save_xml:
        xml_output = json_to_xml(st.session_state.new_dict, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets) 
        response = post_xml_string(xml_output)
        if response is not None:
            st.info(response)
        pretty_xml = minidom.parseString(xml_output).toprettyxml()

        db = load_db()
        db[chapter_name] = pretty_xml

        with open("db.json", "w") as f:
            json.dump(db, f)

        with xml_col.expander("XML content"):
            xml_col.code(pretty_xml)

        st.session_state.table_of_contents = {}
        st.session_state.selected_items = []
        st.session_state.new_dict = {}
        st.session_state.index = ""


 
                
except (KeyError, AttributeError) as e:
    st.info("Click on Generate TOC to get started")
    print(f"Error: {type(e).__name__} - {e}")
db = load_db()
chapter_list = list(db.keys())

if chapter_list:
    delete_button = manage_col.button("Delete Chapter")
    
    

    selected_chapter = manage_col.selectbox("Select a chapter:", chapter_list)
    manage_col.code(db[selected_chapter], language="xml")

    post_button= manage_col.button("POst apoi")
    if post_button:
        url = "https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourse"
        payload = json.dumps({
                                "ImportXML": "<Chapter><NoOfBullets>5</NoOfBullets><NoOfWordsPerBullet>5</NoOfWordsPerBullet><NoOfWordsForVOPerBullet>23</NoOfWordsForVOPerBullet><ChapterName>randon</ChapterName><Topics><Topic><TopicName>Case Information</TopicName><SubTopics><SubTopic><SubTopicName>Case Number</SubTopicName><SubTopicContent>\nThe Case Number is 12345.</SubTopicContent></SubTopic><SubTopic><SubTopicName>District Court</SubTopicName><SubTopicContent>\nThe District Court of XYZ County, State of ABC is the court that is hearing the case between John Doe (Plaintiff) and Jane Smith (Defendant).</SubTopicContent></SubTopic><SubTopic><SubTopicName>XYZ County</SubTopicName><SubTopicContent>\nXYZ County is the location of the District Court in which the case is being heard.</SubTopicContent></SubTopic><SubTopic><SubTopicName>State of ABC</SubTopicName><SubTopicContent>\nThe State of ABC is mentioned in the context information as the location of the District Court of XYZ County.</SubTopicContent></SubTopic></SubTopics></Topic><Topic><TopicName>Parties Involved</TopicName><SubTopics><SubTopic><SubTopicName>Plaintiff</SubTopicName><SubTopicContent>\nThe Plaintiff in this case is John Doe. He is alleging that the Defendant, Jane Smith, intentionally and recklessly caused him bodily harm during an altercation that occurred on June 1, 2022 at approximately 9:00 PM. The Plaintiff suffered bodily harm as a result of the assault, including a broken nose and several cuts and bruises.</SubTopicContent></SubTopic><SubTopic><SubTopicName>Defendant</SubTopicName><SubTopicContent>\nThe Defendant is Jane Smith and she is alleged to have intentionally and recklessly caused bodily harm to the Plaintiff during an altercation on June 1, 2022 at approximately 9:00 PM. The Court finds that the Defendant did commit assault against the Plaintiff and that her actions were intentional and reckless, and that she intended to cause harm to the Plaintiff. The Plaintiff suffered bodily harm as a result of the assault, including a broken nose and several cuts and bruises. The Defendant is therefore liable for the damages suffered by the Plaintiff.</SubTopicContent></SubTopic></SubTopics></Topic><Topic><TopicName>Decision</TopicName><SubTopics><SubTopic><SubTopicName>Overview</SubTopicName><SubTopicContent>\nThe plaintiff, John Doe, brought a claim of assault against the defendant, Jane Smith, alleging that she intentionally and recklessly caused him bodily harm during an altercation that occurred on June 1, 2022, at approximately 9:00 PM. After a review of the evidence presented at trial, including testimony from the plaintiff and the defendant, the court found that the defendant did commit assault against the plaintiff. The court found that the defendant's actions were intentional and reckless, and that she intended to cause harm to the plaintiff. The plaintiff suffered bodily harm as a result of the assault, including a broken nose and several cuts and bruises. The defendant's actions were not justified under any circumstances, and she is therefore liable for the damages suffered by the plaintiff.</SubTopicContent></SubTopic><SubTopic><SubTopicName>Evidence Review</SubTopicName><SubTopicContent>\nThe court reviewed evidence presented at trial, including testimony from the plaintiff and the defendant.</SubTopicContent></SubTopic><SubTopic><SubTopicName>Findings</SubTopicName><SubTopicContent>\nThe court finds that the defendant did commit assault against the plaintiff. The defendant's actions were intentional and reckless, and she intended to cause harm to the plaintiff. The plaintiff suffered bodily harm as a result of the assault, including a broken nose and several cuts and bruises. The defendant's actions were not justified under any circumstances, and she is therefore liable for the damages suffered by the plaintiff.</SubTopicContent></SubTopic><SubTopic><SubTopicName>Judgement</SubTopicName><SubTopicContent>\nThe court finds that the defendant did commit assault against the plaintiff. The court further finds that the plaintiff suffered bodily harm as a result of the assault, including a broken nose and several cuts and bruises. The defendant's actions were not justified under any circumstances, and she is therefore liable for the damages suffered by the plaintiff. Based on the foregoing, it is hereby ordered that judgement be entered in favor of the plaintiff and against the defendant in the amount of $10,000 in compensatory damages and $5,000 in punitive damages. The defendant is also ordered to pay all costs associated with this lawsuit.</SubTopicContent></SubTopic></SubTopics></Topic></Topics></Chapter>"
                                })
        headers = {
                    'Content-Type': 'application/json'
                    }


        response = requests.request("POST", url, headers=headers, data=payload)
        st.write(response)
        print(response)
        st.write(response.text)




    if delete_button:
        if delete_chapter(selected_chapter):
            manage_col.success(f"Chapter {selected_chapter} deleted successfully.")
            db = load_db()
            chapter_list = list(db.keys())
            if chapter_list:
                selected_chapter = manage_col.selectbox("Select a chapter:", chapter_list)
                manage_col.code(db[selected_chapter], language="xml")
            else:
                manage_col.warning("No chapters found. Upload a chapter and save its XML first.")
        else:
            manage_col.error(f"Failed to delete chapter {selected_chapter}.")

else:
    manage_col.warning("No chapters found. Upload a chapter and save its XML first.")

