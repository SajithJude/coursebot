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
import streamlit.components.v1 as components
import extra_streamlit_components as stx





st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("CourseBOT for PDF")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"


PDFReader = download_loader("PDFReader")

loader = PDFReader()


if not os.path.exists("images"):
    os.makedirs("images")





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



video_type = st.radio("Type of Video", ["Case Study", "eLearning"], horizontal= True)


if video_type == "elearning":

    ######################       defining tabs      ##########################################

    # upload_col, refine_toc,  extract_col, miss_col, edit_col,voice_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__","⚪ __missing_Contents__", "⚪ __Edit Contents__", "⚪ Voice Over__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])
    upload_col, toc_col,  extract_col, voice_col, xml_col = st.tabs(["⚪ __Upload PDF__","⚪ __Video Structure__", "⚪ __Extract Content__", "⚪ __Edit__", "⚪ __Images__"])




    ######################       Upload chapter column      ##########################################


    uploaded_file = upload_col.file_uploader("Upload a PDF file", type="pdf")
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
            upload_col.success("Click on Tab 'Video Structure'")
            # clear_images_folder()
            # clear_pages_folder()
        # read PDF file
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

    crsnm = upload_col.text_input("Enter Course Name")
    savnext = upload_col.button("Save Project")
    if savnext:
        if "index" in st.session_state:
            if crsnm != "":
                if "crsnm" not in st.session_state:
                    st.session_state.crsnm = crsnm

                lovo = st.session_state.index.query(f"Generate a voice over script for the following learning objectives for this book").response.strip()
                descrip  = st.session_state.index.query(f"Generate a Course Description with word count of minimum 20 words and maximum 25 words (Do not exceed more than 25 words)").response.strip()
                cvo  = st.session_state.index.query(f"Generate a Course Description voice over script with word count of 50").response.strip()
                lo = st.session_state.index.query(f"Generate 5 learning objectives seperated by a ~ symbol between each objective for this book, the word count should be minimum-6 words and maximum-12 words, do not add numbers to the objectives ").response.strip()
                lo_input = [lo.split("~")]

                if "descrip" not in st.session_state:
                    st.session_state.descrip = descrip

                if "cvo" not in st.session_state:
                    st.session_state.cvo = cvo

                if "lovo" not in st.session_state:
                    st.session_state.lovo = lovo

                if "lo_input" not in st.session_state:
                    st.session_state.lo_input = lo_input
                upload_col.success("Project saved successfully.\nGo to Table of Content tab to create Table of content")
            else :
                upload_col.write("Please enter a course name")
    
        else:
            if crsnm == "":
                upload_col.write("Please upload a PDF & enter a course name")

            else :
                upload_col.write("Please upload a PDF")




    ###################### tab 2 ################
    toc_option = toc_col.radio("How do you want to base your course structure", ("Paste Table of Contents", "AI Generated"), horizontal=True)
    # toc_col.info("Choose AI Generated if you want AI to suggest a course structure, modify (it if needed) after pasting it on the right and click process")
    # pastecol, toc_col = toc_col.columns(2,gap="medium")


    try:

        if toc_option == "Paste Table of Contents":

            toc_input = toc_col.text_area("Copy Paste TOC from document")
            
            if toc_col.button("Process Structure"):
                if toc_input != "":
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
                else :
                    toc_col.write("please copy and paste the Table of content from document")

        elif toc_option == "AI Generated":
            # toc_col,pastecol  = toc_col.columns(2,gap="medium")
            # copycol.write("AI Generated Structure")
            if "sample_table" not in st.session_state:
                with st.spinner("Please wait till the A.I Generates the course structure "):
                    sample_table = st.session_state.index.query(f"Generate a course structure/Table of contents with only sections of topics and subtopics for this document, where each topic should have exactly 5 subtopics").response.strip()
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
        str_toc =    (toc_res)
        table_of_contents = json.loads(str(str_toc))
        st.session_state.table_of_contents = table_of_contents
        toc_col.write(st.session_state.table_of_contents)
        # toc_col.error("Invalid JSON format. Please check your input.")
        toc_col.error(e)

    except :
        toc_col.write("Please upload a chapter")






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
        #st.write(st.session_state.dictionary)
        for topic in st.session_state.dictionary["Topics"]:
            # extract_col.write(topic)
            # topic_sum = st.session_state.index.query(f"Generate Topic Summary description of {topic_summary_limit} words by summarizing the information beloning to the following section {topic['Topic_Name']}").response.strip()
            # extract_col.info(topic_sum)
            # Voice_topic_sum = st.session_state.index.query(f"Generate Topic Summary voice over script of {topic_summary_voiceover_limit} words by summarizing the information beloning to the following section {topic['Topic_Name']}").response.strip()
            # extract_col.info(Voice_topic_sum)
            # topic["Topic_Summary"] = topic_sum
            # topic["Topic_Summary_VoiceOver"] = Voice_topic_sum

            for subtopic in topic["Subtopics"]:

                voiceovers = st.session_state.index.query(f"Generate a voice over script as a single string for the section named {subtopic['Subtopic_Name']} .").response.strip()
                # subtopic["VoiceOver"] = voiceovers.split("~")[:num_bullets_per_slide]  # assume voice overs are comma-separated
                subtopic["VoiceOver"] = voiceovers
                extract_col.write(subtopic["VoiceOver"])

                bullets = st.session_state.index.query(f"Generate {num_bullets_per_slide} Bullet points as a single string, for the content in the following script {voiceovers}\n, the total word count should be within 30-40 words and should not exceed the limit").response.strip()
                # subtopic["Bullets"] = bullets.split("~")[:num_bullets_per_slide]  # assume bullets are comma-separated
                subtopic["Bullets"] = bullets
                extract_col.write(subtopic["Bullets"])

                
        #st.write(st.session_state.dictionary)
        st.session_state.button_clicked = False
        st.session_state.processed_all_items = True




    ######################       voice over      ##########################################

    try:

        course_name = voice_col.text_input('Course Name', st.session_state.dictionary['Course']['Course_Name'])
        course_description = voice_col.text_input('Course Description', st.session_state.dictionary['Course']['Course_Description'])

        objectives = st.session_state.dictionary['Course_Objectives'][0]['Objective'][0]
        for i, obj in enumerate(objectives):
            objectives[i] = voice_col.text_input(f'Objective {i+1}', obj)

        topics = st.session_state.dictionary['Topics'][0]['Subtopics']
        for i, topic in enumerate(topics):
            with st.expander(f'Topic {i+1}'):
                topic_name = voice_col.text_input('Topic Name', topic['Subtopic_Name'])
                topic_bullets = voice_col.text_input('Topic Bullets', topic['Bullets'])
                topic_voiceover = voice_col.text_input('Topic Voiceover', topic['VoiceOver'])
                topic_image = voice_col.text_input('Topic Image', topic['Image'])

    except:
        print("Error in edit tabs")


    if voice_col.button("Save Changes"):
        save_dictionary_as_json()

        st.session_state.dictionary

else:

    # Uploadtab, toctab,  extractTab, synthesiaTab = st.tabs(["⚪ __Upload PDF__","⚪ __Video Structure__", "⚪ __Extract Contents__", "⚪ __Create Video__"])
    
    steps = ["1","2","3","4"]
    bar = stx.stepper_bar(steps=steps)
    current_step = st.empty()
    # current_step=0

    # current_step.write(bar)
    if bar == 0:
        uploaded_file = Uploadtab.file_uploader("Upload a PDF file", type="pdf")
    # toc_option = Uploadtab.radio("Choose a method to provide TOC", ("Generate TOC", "Copy Paste TOC"))

        if uploaded_file is not None:

                # index = 
                if "index" not in st.session_state:
                    st.session_state.index = process_pdf(uploaded_file)

                Uploadtab.success("Index created successfully")

                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
        pass 
        # Uploadtab = current_step
        
    elif bar == 1:
            if toctab.button("Get Video structure"):
                query = f"Generate an optimal video content structure with 10 scenes and titles for a case study video from this document"
                course_structure = st.session_state.index.query(query).response
                if "course_structure" not in st.session_state:
                    st.session_state.course_structure = course_structure

                # toctab.write(st.session_state.course_structure)
            
            try:
                if st.session_state.course_structure is not None:    
                    cs_format = """
                    {
                    "CourseStructure": {
                        "Scenes": [
                        {
                            "Scene1": {
                            "Title": "description or URL of image",
                            "TextOverlay": "description or text to be shown",
                            "Voiceover": "description or script of voiceover"
                            },
                            "Scene2": {
                            "Title": "description or URL of image",
                            "TextOverlay": "description or text to be shown",
                            "Voiceover": "description or script of voiceover"
                            },
                            "Scene3": {
                            "Title": "description or URL of image",
                            "TextOverlay": "description or text to be shown",
                            "Voiceover": "description or script of voiceover"
                            }
                            // Add more scenes as needed
                        }
                        ]
                    }
                    }
                    """
                    modify_cs = toctab.text_area("Modify the structure if needed", value=st.session_state.course_structure,  height=400)
                    if toctab.button("Confirm Structure"):
                        convert_prompt = "Convert the following content structure into a json string, use the JSON format given bellow:\n"+ "Content Structure:\n"+ modify_cs.strip() + "\n JSON format:\n"+ str(cs_format) + ". Output should be a valid JSON string."
                        json_cs = call_openai(convert_prompt)
                        toctab.write(json_cs)
                        cs_dictionary = json.loads(json_cs.strip())
                        if "cs_dictionary" not in st.session_state:
                            st.session_state.cs_dictionary = cs_dictionary
                        toctab.write(st.session_state.cs_dictionary)

            except:
                print("Upload a document to get started")
            pass

        # toctab = current_step

    # elif bar == 1:
    #     extractTab = current_step

    # elif bar == 1:
    #     synthesiaTab = current_step


    uploaded_file = Uploadtab.file_uploader("Upload a PDF file", type="pdf")
    # toc_option = Uploadtab.radio("Choose a method to provide TOC", ("Generate TOC", "Copy Paste TOC"))

    if uploaded_file is not None:

            # index = 
            if "index" not in st.session_state:
                st.session_state.index = process_pdf(uploaded_file)

            Uploadtab.success("Index created successfully")

            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

    
###################### video structure ##########################


    if "index" in st.session_state:
        vid_duration = toctab.slider("How long is the video ?")
        # if "vid_duration" not in st.session_state:
        #     st.session_state.vid_duration = vid_duration

        # video_type = st.radio("Type of Video", ["casestudy", "elearning", "custom"])
        # if video_type == "custom":
        #     video_type = st.text_input("What kind of video content would you like to make ?")
        



####################   extract tab #####################################

if extractTab.button("Get data"):
  for scene in st.session_state.cs_dictionary["CourseStructure"]["Scenes"]:
    for scene_name, scene_data in scene.items():
        opening_shot = scene_data["Title"]
        overlay = st.session_state.index.query(f"Generate some short text content to display in a slide titled as {opening_shot}").response.strip()
        voiceover = st.session_state.index.query(f"Generate a voice over script as a single string to narrate in a slide Titled  {opening_shot}").response.strip()
        extractTab.write(scene_name)
        extractTab.info(overlay)
        extractTab.info(voiceover)

        scene_data["TextOverlay"] = overlay
        scene_data["Voiceover"] = voiceover
  extractTab.write(st.session_state.cs_dictionary)




#################### synthesia tab ###############################################

name_vid =synthesiaTab.text_input("Name of video")

if synthesiaTab.button("Create Video Part 1"):

    headers = {
                    'Authorization': "5ad72dcaafb054f6c163e2feb9334539",
                    'Content-Type': 'application/json'
                }




    api_data = {
        "title": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["Title"],
        "description": "First part with lo cn cd and top 1",
        "visibility": "public",
        "templateId": "1419387f-2154-4fff-a7f1-b2d6c9c2fca8",
        "templateData": {
            "Course_Name": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["Title"],
            "Course_Description": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["TextOverlay"],
            "intovo": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["Voiceover"],

            "Subtopic_1": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["Title"],
            "Copy_1": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["TextOverlay"],
            "script1": st.session_state.cs_dictionary["CourseStructure"]["Scenes"][0]["Scene1"]["Voiceover"],


            # Add similar mappings for other fields as needed.
        },
        "test": True,
        "callbackId": "john@example.com"
    }
    with synthesiaTab.expander("api_data"):
        st.write(api_data)

    # Make the API request
    response = requests.post('https://api.synthesia.io/v2/videos/fromTemplate', headers=headers, data=json.dumps(api_data))
    if response.status_code == 201:
        synthesiaTab.info('Sample scene video creation process started successfully.')
        video_id = response.json()['id']
        synthesiaTab.write(f'Video ID for Sample scene: {video_id}')
        synthesiaTab.code(video_id)
        if "video_id" not in st.session_state:
            st.session_state.video_id = video_id
        url = f"https://share.synthesia.io/embeds/videos/{video_id}"
        synthesiaTab.write(url)
        iframe_html = f""" <div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src="{url}" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"""
        components.html(iframe_html,height=600)
        # frame = f"<div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src=" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"



    else:
        synthesiaTab.write('An error occurred during the video creation process for Sample scene.')
        synthesiaTab.write(f'Response status code: {response.status_code}')
        synthesiaTab.write(f'Response content: {response.content}')

