import streamlit as st
from llama_index import (
    GPTVectorStoreIndex, Document, SimpleDirectoryReader,
    QuestionAnswerPrompt, LLMPredictor, ServiceContext
)
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile
import base64
import io
from PIL import Image
import ast
import os
import glob
import openai
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import requests
import zipfile
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("CourseBot for PDF's")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"


PDFReader = download_loader("PDFReader")

loader = PDFReader()


if not os.path.exists("images"):
    os.makedirs("images")



if "dictionary" not in st.session_state:
    st.session_state.dictionary = {}

# Function to save dictionary as JSON file
def save_dictionary_as_json():
    course_name = st.session_state.crsnm
    json_data = json.dumps(st.session_state.dictionary, indent=4)

    # Create a directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Save the JSON file
    filename = f"output/{course_name}.json"
    with open(filename, "w") as file:
        file.write(json_data)

    st.sidebar.success(f"JSON file saved as: {filename}")



def call_openai3(source):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=source,
        temperature=0.1,
        max_tokens=3500,
        top_p=1,
        frequency_penalty=0.3,
        presence_penalty=0
    )
    return response.choices[0].text



def call_openai(source):
    messages=[{"role": "user", "content": source}]

    response = openai.ChatCompletion.create(
        model="gpt-4-0314",
        max_tokens=7000,
        temperature=0.1,
        messages = messages
       
    )
    return response.choices[0].message.content



# import xml.etree.ElementTree as ET

# import xml.etree.ElementTree as ET
def create_xml(dictionary):
    root = ET.Element("Slides")

    # Slide 1: Course
    course = ET.SubElement(root, "Slide1")
    ET.SubElement(course, "Slide_Name").text = "Course_Name"
    ET.SubElement(course, "Course_Name").text = dictionary["Course"]["Course_Name"]
    ET.SubElement(course, "Course_Description").text = dictionary["Course"]["Course_Description"]
    ET.SubElement(course, "VoiceOver").text = dictionary["Course"]["VoiceOver"]

    # Slide 2: Topics
    topics = ET.SubElement(root, "Slide2")
    ET.SubElement(topics, "Slide_Name").text = "Topics"
    for topic in dictionary["Topics"]:
        ET.SubElement(topics, "Topic").text = topic["Topic_Name"]

    # Slide 3: Course Objectives
    objectives = ET.SubElement(root, "Slide3")
    ET.SubElement(objectives, "Slide_Name").text = "Course_Objectives"
    for objective in dictionary["Course_Objectives"]:
        ET.SubElement(objectives, "Objective").text = objective["Objective"]
        ET.SubElement(objectives, "VoiceOver").text = objective["VoiceOver"]

    # Other slides: One per topic + subtopic
    slide_num = 4
    for topic in dictionary["Topics"]:
        # Slide: Topic and its Subtopics
        topic_slide = ET.SubElement(root, f"Slide{slide_num}")
        ET.SubElement(topic_slide, "Slide_Name").text = "Topic_Name"
        ET.SubElement(topic_slide, "Topic_Name").text = topic["Topic_Name"]
        for subtopic in topic["Subtopics"]:
            ET.SubElement(topic_slide, "Subtopic_Name").text = str(subtopic["Subtopic_Name"])

        slide_num += 1

        # Slides: One per Subtopic
        for subtopic in topic["Subtopics"]:
            subtopic_slide = ET.SubElement(root, f"Slide{slide_num}")
            ET.SubElement(subtopic_slide, "Slide_Name").text = "Subtopic"
            ET.SubElement(subtopic_slide, "Subtopic").text = str(subtopic["Subtopic_Name"])
            bcount = 1
            for bullet in subtopic["Bullets"]:
                ET.SubElement(subtopic_slide, f"Bullet_{bcount}").text = bullet
                bcount+=1
            voc =1
            voel = ET.SubElement(subtopic_slide, "VoiceOver")
            for voiceover in subtopic["VoiceOver"]:
                ET.SubElement(voel, f"VoiceOver_{voc}").text = voiceover
                voc+=1

            slide_num += 1

        # Slide: Topic Summary
        summary_slide = ET.SubElement(root, f"Slide{slide_num}")
        ET.SubElement(summary_slide, "Slide_Name").text = "Topic_Summary"
        ET.SubElement(summary_slide, "Topic_Summary").text = topic["Topic_Summary"]
        ET.SubElement(summary_slide, "VoiceOver").text = topic["Topic_Summary_VoiceOver"]

        slide_num += 1

    # Final slide: Congratulations
    final_slide = ET.SubElement(root, f"Slide{slide_num}")
    ET.SubElement(final_slide, "Slide_Name").text = "Congratulations"
    ET.SubElement(final_slide, "Message").text = "Congratulations!"

    # Convert to XML string
    xml_str = ET.tostring(root, encoding='unicode')
    return xml_str



def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=3900))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    
    if "index" not in st.session_state:
        index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
        retriever = index.as_retriever(retriever_mode='embedding')
        index = RetrieverQueryEngine(retriever)
        st.session_state.index = index
    # st.session_state.index = index
    return st.session_state.index
        

######################       defining tabs      ##########################################

# upload_col, refine_toc,  extract_col, miss_col, edit_col,voice_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__","⚪ __missing_Contents__", "⚪ __Edit Contents__", "⚪ Voice Over__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])
upload_col, toc_col,  extract_col, voice_col, xml_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Table Of Contents__", "⚪ __Extract Contents__", "⚪ __XML__", "⚪ __Images__"])




######################       Upload chapter column      ##########################################


uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")
# toc_option = upload_col.radio("Choose a method to provide TOC", ("Generate TOC", "Copy Paste TOC"))
forma = """"{
  "Topics": [
    {
      "n.n Topic ": [
        "n.n.n Subtopic ",
        "n.n.n Subtopic ",
      ]
    }
  ]
}

"""
if uploaded_file is not None:
        # clear_all_json_files()

        # index = 
        if "index" not in st.session_state:
            st.session_state.index = process_pdf(uploaded_file)

        upload_col.success("Index created successfully")
        # clear_images_folder()
        # clear_pages_folder()
    # read PDF file
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

crsnm = upload_col.text_input("Enter Course Name")
savnext = upload_col.button("Save Project")
if savnext:
    if "crsnm" not in st.session_state:
        st.session_state.crsnm = crsnm

    lovo = st.session_state.index.query(f"Generate a voice over script for the following learning objectives for this book").response.strip()
    descrip  = st.session_state.index.query(f"Generate a Course Description with word count of 30").response.strip()
    cvo  = st.session_state.index.query(f"Generate a Course Description voice over script with word count of 50").response.strip()
    lo_input = st.session_state.index.query(f"What are the learning objectives of this book ").response.strip()
        

    if "descrip" not in st.session_state:
        st.session_state.descrip = descrip

    if "cvo" not in st.session_state:
        st.session_state.cvo = cvo

    if "lovo" not in st.session_state:
        st.session_state.lovo = lovo

    if "lo_input" not in st.session_state:
        st.session_state.lo_input = lo_input




###################### tab 2 ################
toc_option = toc_col.radio("How do you want to base your course structure", ("Paste Table of Contents", "AI Generated"), horizontal=True)
# toc_col.info("Choose AI Generated if you want AI to suggest a course structure, modify (it if needed) after pasting it on the right and click process")
# pastecol, toc_col = toc_col.columns(2,gap="medium")


try:

    if toc_option == "Paste Table of Contents":

        toc_input = toc_col.text_area("Copy Paste TOC from document")

        if toc_col.button("Process Structure"):
            # try:
                # table_of_contents = json.loads(toc_input)
            with st.spinner('Please wait, it might take a while to process the Course structure'):
                toc_res = "Convert the following table of contents into a json string, use the JSON format given bellow:\n"+ "Table of contents:\n"+ toc_input.strip() + "\n JSON format:\n"+ str(forma) + ". Output should be a valid JSON string."
                str_toc = call_openai(toc_res)
                str_to = str(str_toc)
            # st.write(str_to)
            table_of_contents = json.loads(str_to.strip())
            st.session_state.table_of_contents = table_of_contents

            # if "table_of_contents" not in st.session_state:
            toc_col.success("TOC loaded, Go to the next tab")
            toc_col.write(st.session_state.table_of_contents)


    elif toc_option == "AI Generated":
        # toc_col,pastecol  = toc_col.columns(2,gap="medium")
        # copycol.write("AI Generated Structure")
        if "sample_table" not in st.session_state:
            with st.spinner("Please wait till the A.I Generates the course structure "):
                sample_table = st.session_state.index.query(f"Generate a course structure/Table of contents with only sections of topics and subtopics for this document").response.strip()
                st.session_state.sample_table = sample_table


        toc_input = toc_col.text_area("Make Neccessary Edits to the AI generated structure and click Save Structure",value=str(st.session_state.sample_table))

        if toc_col.button("Save Structure"):
            # try:
                # table_of_contents = json.loads(toc_input)
            with st.spinner('Please wait, it might take a while to process the Course structure'):
                toc_res = "Convert the following table of contents into a json string, use the JSON format given bellow:\n"+ "Table of contents:\n"+ toc_input.strip() + "\n JSON format:\n"+ str(forma) + ". Output should be a valid JSON string."
                str_toc = call_openai(toc_res)
                str_to = str(str_toc)
            # st.write(str_to)
            table_of_contents = json.loads(str_to.strip())
            st.session_state.table_of_contents = table_of_contents

            # if "table_of_contents" not in st.session_state:
            toc_col.success("TOC loaded, Go to the next tab")
            toc_col.write(st.session_state.table_of_contents)

except json.JSONDecodeError as e:
    str_toc = call_openai(toc_res)
    table_of_contents = json.loads(str(str_toc))
    st.session_state.table_of_contents = table_of_contents
    toc_col.write(st.session_state.table_of_contents)
    # toc_col.error("Invalid JSON format. Please check your input.")
    toc_col.error(e)






pagecol, ecol = extract_col.columns([2,5],gap="large")

# # Topic Summary
topic_summary_limit = pagecol.number_input("Topic Summary Word Count Limit", value=30, min_value=1)

# Topic Summary VoiceOver
topic_summary_voiceover_limit = pagecol.number_input("Topic Summary VoiceOver Word Count Limit", value=50, min_value=1)

# Number of Bullets per Slide
num_bullets_per_slide = pagecol.number_input("Number of Bullets per Slide", value=4, min_value=1)

# Number of Words per Bullet
num_words_bullet = pagecol.number_input("Number of Words per Bullet", value=10, min_value=1)

# Bullet VoiceOver
bullet_voiceover_limit = pagecol.number_input("VoiceOver per Bullet Word Count Limit", value=20, min_value=1)
# # aaaa
# Course Description
course_description_limit = pagecol.number_input("Course Description Word Count Limit", value=30, min_value=1)

# Course Description VoiceOver
course_description_voiceover_limit = pagecol.number_input("Course Description VoiceOver Word Count Limit", value=50, min_value=1)




if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

if "processed_all_items" not in st.session_state:
    st.session_state.processed_all_items = False
if ecol.button("Extract and Generate"):
    st.session_state.button_clicked = True
            
    if "dictionary" not in st.session_state:
        st.session_state.dictionary = {
    "Course": {
        "Course_Name": st.session_state.crsnm,
        "Course_Description": st.session_state.descrip,
        "VoiceOver": st.session_state.cvo
    },
    "Topics": [],
    "Course_Objectives": [
        {
        "Objective": st.session_state.lo_input,
        "VoiceOver": st.session_state.lovo
        },
    ]
    }
    
    # if "table_of_contents" in st.session_state:
    # Convert topics to new forma
    for topic in st.session_state.table_of_contents["Topics"]:
        for topic_name, subtopics in topic.items():
            new_topic = {
            "Topic_Name": topic_name,
            "Subtopics": [],
            "Topic_Summary": "",
            "Topic_Summary_VoiceOver": ""
            }

            for subtopic in subtopics:
                new_subtopic = {
                    "Subtopic_Name": subtopic,
                    "Bullets": [],
                    "VoiceOver": [],
                    "Image": ""
                }
            new_topic["Subtopics"].append(new_subtopic)
        st.session_state.dictionary["Topics"].append(new_topic)


# gen = ecol.button("Extract and Generate")
if st.session_state.button_clicked and not st.session_state.processed_all_items:
    
    for topic in st.session_state.dictionary["Topics"]:

        topic_sum = st.session_state.index.query(f"Generate Topic Summary description of {topic_summary_limit} words by summarizing the information beloning to the following section {topic['Topic_Name']}").response.strip()
        extract_col.info(topic_sum)
        Voice_topic_sum = st.session_state.index.query(f"Generate Topic Summary voice over script of {topic_summary_voiceover_limit} words by summarizing the information beloning to the following section {topic['Topic_Name']}").response.strip()
        extract_col.info(Voice_topic_sum)
        topic["Topic_Summary"] = topic_sum
        topic["Topic_Summary_VoiceOver"] = Voice_topic_sum

        for subtopic in topic["Subtopics"]:

            bullets = st.session_state.index.query(f"Generate {num_bullets_per_slide} Bullet points (Each bullet should be a valid string) that are seperated by a '~' symbol in between, for the section named {subtopic['Subtopic_Name']}\n, word count per Bullet is {num_words_bullet}.").response.strip()
            subtopic["Bullets"] = bullets.split("~")  # assume bullets are comma-separated
            extract_col.write(subtopic["Bullets"])

            voiceovers = st.session_state.index.query(f"Generate {num_bullets_per_slide} comma-seperated voice over's (each voice over should be a valid string) that are seperated by a '~' symbol in between, for the section named {subtopic['Subtopic_Name']}\n, Word count per voice over is {bullet_voiceover_limit}.").response.strip()
            subtopic["VoiceOver"] = voiceovers.split("~")  # assume voice overs are comma-separated
            extract_col.write(subtopic["VoiceOver"])
    st.session_state.button_clicked = False
    st.session_state.processed_all_items = True




######################       voice over      ##########################################



if voice_col.button("Show XML"):
    
    xml = create_xml(st.session_state.dictionary)
    pretty_xml = minidom.parseString(xml).toprettyxml()
    

    voice_col.code(pretty_xml)
    save_dictionary_as_json()



######################       export generated xml      ##########################################


# try:
#     # with 
#     ondu, naduvan, rendu   = xml_col.columns([4,3,4],gap="large")

#     ondu.write("### Select Images")
#     ondu.write("")
#     ondu.write("")

#     left, right = ondu.columns(2)
#     image_topic = left.selectbox("Select a topic", list(st.session_state.new_dict.keys()),label_visibility="collapsed")
#     add_to_topic = right.button("Add Image to Topic")

# # Dropdown menu for selecting a subtopic based on the selected topic
#     image_subtopic = left.selectbox("Select a subtopic", [subtopic["Subtopic"] for subtopic in st.session_state.new_dict[image_topic]["Subtopics"]],label_visibility="collapsed")
#     add_to_subtopic = right.button("Add image to Subtopic")

#     image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
#     selected_images = []
#     # for image in image_files:
#     expander = ondu.expander("Select images")
#     n_pages = 20

#     image_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
#     page_index = ondu.number_input("Enter page number", min_value=1, max_value=n_pages, value=1)

#     with ondu.expander(f"Page {page_index}", expanded=True):
#         image_files = [f for f in os.listdir("images") if f.startswith(f'image_page{page_index}_') and f.endswith(tuple(image_exts))]
#         # if image_files:
#         for image_filename in image_files:
#             file_path = os.path.join("images", image_filename)
#             if os.path.isfile(file_path):
#                 ondu.image(file_path, caption=os.path.basename(file_path),width=150)
#             else:
#                 st.warning(f"Image not found: {os.path.basename(file_path)}")
#         # else:
#         #     st.warning("No images found for this page.")
    
#     selected_image = image_filename

#     if add_to_topic:
#         if "img" not in st.session_state.new_dict[image_topic]:
#             st.session_state.new_dict[image_topic]["img"] = []
#         st.session_state.new_dict[image_topic]["img"].append(selected_image)
#         ondu.success(f"Image {selected_image} added to topic {image_topic}")

#     if add_to_subtopic:
#         for subtopic in st.session_state.new_dict[image_topic]["Subtopics"]:
#             if subtopic["Subtopic"] == image_subtopic:
#                 if "img" not in subtopic:
#                     subtopic["img"] = []
#                 subtopic["img"].append(selected_image)
#                 ondu.success(f"Image {selected_image} added to subtopic {image_subtopic}")
#                 break

#     naduvan.write("### Compare ")
#     pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

#     # if pages_files:
#     selected_page = naduvan.number_input("Compare Images",step=1)
#     selected_image = f"page-{selected_page}.png"
#     # Display the selected image
#     if selected_image:
#         naduvan.image(os.path.join("pages", selected_image), use_column_width=True)
#     else:
#         naduvan.warning("No images found in the 'pages' folder.")




#     rendu.write("### Configure ")
#     # chapter_name = rendu.text_input("enter chapter name")
#     # r1,r2 = rendu.columns(2)

#     # NoOfBullets = r1.text_input("No. of Bullets per Sub Topic")
#     # NoOfWordsPerBullet = r1.text_input("No. of words per Bullet")
#     # NoOfWordsForVOPerBullet = r1.text_input("No. of words for Voice Over per Bullet")
#     save_xml = rendu.button("Save XML")
    


#     if save_xml:

#         # if "edited" not in st.session_state:
#         #     st.session_state.edited = st.session_state.missing
#         #xml_col.write(st.session_state.new_dict)

#         xml_output = json_to_xml(st.session_state.new_dict, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets) 
#         pretty_xml = minidom.parseString(xml_output).toprettyxml()

#         xml_file_path = os.path.join("images", f"{chapter_name}.xml")
#         with open(xml_file_path, "w") as xml_file:
#             xml_file.write(pretty_xml)
#         # rendu.success(f"XML file saved as {xml_file_path}")

#         with xml_col.expander("XML content"):
#             xml_col.code(pretty_xml)

#         # Zip the entire "images" folder with its contents
#         def zipdir(path, ziph):
#             for root, dirs, files in os.walk(path):
#                 for file in files:
#                     ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))

#         zip_file_path = f"images/{chapter_name}.zip"
#         with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#             zipdir("images", zipf)
#         rendu.success(f"Zipped folder saved as {zip_file_path}")

#         # st.session_state.table_of_contents = {}
#         # st.session_state.selected_items = []
#         # st.session_state.new_dict = {}
#         # st.session_state.index = ""
#         # st.session_state.new_dict = {}
 
                
# except (KeyError,NameError, AttributeError) as e:
#     print("Error saving XML")
#     print(f"Error: {type(e).__name__} - {e}")




# # ######################      Manage XML      ##########################################

# # db = load_db()
# # chapter_list = list(db.keys())

# # if chapter_list:

# #     filesinsidefolder = manage_col.selectbox("Select a zip file", [f for f in os.listdir("images") if f.endswith(('.zip'))])

# #     if filesinsidefolder and filesinsidefolder.endswith('.zip'):
# #         file_path = os.path.join("images", filesinsidefolder)
# #         with open(file_path, "rb") as f:
# #             file_bytes = f.read()
# #         manage_col.download_button(
# #             label="Download Zip File",
# #             data=file_bytes,
# #             file_name=filesinsidefolder,
# #             mime="application/zip",
# #         )
   
# #     else:
# #         manage_col.warning("No file selected.")



# #     selected_chapter = manage_col.selectbox("Select a chapter first:", chapter_list)
# #     delete_button = manage_col.button("Delete Chapter")
# #     post_button= manage_col.button("Continue with CourseBOT 2")


# #     if post_button:
# #         url = "https://coursebot2.flipick.com/couresbuilderapi/api/Course/ImportCourse"
# #         payload = json.dumps({
# #                                 "ImportXML": str(db[selected_chapter])
# #                                 })
# #         headers = {
# #                     'Content-Type': 'application/json'
# #                     }


# #         response = requests.request("POST", url, headers=headers, data=payload)
        
# #         print(response)
# #         response_dict = json.loads(response.text)

# #         url_to_launch = response_dict["result"]["urlToLaunch"]
# #         manage_col.subheader("Click on the url bellow to continue.")
# #         manage_col.write(url_to_launch)




# #     if delete_button:
# #         if delete_chapter(selected_chapter):
# #             manage_col.success(f"Chapter {selected_chapter} deleted successfully.")
# #             db = load_db()
# #             chapter_list = list(db.keys())
# #             if chapter_list:
# #                 selected_chapter = manage_col.selectbox("Select a chapter:", chapter_list)
# #                 manage_col.code(db[selected_chapter], language="xml")
# #             else:
# #                 manage_col.warning("No chapters found. Upload a chapter and save its XML first.")
# #         else:
# #             manage_col.error(f"Failed to delete chapter {selected_chapter}.")

# # else:
# #     manage_col.warning("No chapters found. Upload a chapter and save its XML first.")