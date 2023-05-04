import streamlit as st
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader, QuestionAnswerPrompt, LLMPredictor, ServiceContext
import json
from langchain import OpenAI
from llama_index import download_loader
from tempfile import NamedTemporaryFile

import io
import fitz
from PIL import Image
import ast
import os
import glob
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
import zipfile


from langchain import OpenAI
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="collapsed")
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("CourseBot")
st.caption("AI-powered course creation made easy")
DATA_DIR = "data"

PDFReader = download_loader("PDFReader")

loader = PDFReader()


if not os.path.exists("images"):
    os.makedirs("images")

# Create the "pages" folder if it doesn't exist
if not os.path.exists("pages"):
    os.makedirs("pages")


def call_openai(source):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=source,
        temperature=0.56,
        max_tokens=2066,
        top_p=1,
        frequency_penalty=0.35,
        presence_penalty=0
    )
    return response.choices[0].text

def clear_all_json_files():
    """Clear all JSON files in all directories under the current working directory"""
    
    root_directory = os.path.abspath(os.getcwd())
    
    # Iterate over all files and directories under the root directory
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # Iterate over all files in the current directory
        for filename in filenames:
            # Check if the file has a .json extension
            if filename.endswith('.json'):
                # Open the JSON file, clear its contents, and save the empty file
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'w') as json_file:
                    json.dump({}, json_file)

def clear_images_folder():
    for file in os.listdir("images"):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            os.remove(os.path.join("images", file))

def clear_pages_folder():
    for file in os.listdir("pages"):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            os.remove(os.path.join("pages", file))


def update_json(topic_data):
    with open("output.json", "w") as f:
        st.session_state.toc = {"Topics": [{k: v} for k, v in topic_data.items()]}
        json.dump({"Topics": [{k: v} for k, v in topic_data.items()]}, f)


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


def json_to_xml(json_data, chapter_name):
    chapter = Element('Chapter')


    chapter_name_element = SubElement(chapter, 'ChapterName')
    chapter_name_element.text = chapter_name

    topics = SubElement(chapter, 'Topics')

    for topic_name, topic_info in json_data.items():
        topic = SubElement(topics, 'Topic')
        topic_name_element = SubElement(topic, 'TopicName')
        topic_name_element.text = topic_name

        # Add img tag for the topic if it exists
        if "img" in topic_info:
            for img_path in topic_info["img"]:
                img_element = SubElement(topic, 'img')
                img_element.text = img_path

        subtopics = SubElement(topic, 'SubTopics')
        for subtopic_info in topic_info['Subtopics']:
            subtopic = SubElement(subtopics, 'SubTopic')

            subtopic_name = SubElement(subtopic, 'SubTopicName')
            subtopic_name.text = subtopic_info['Subtopic']

            subtopic_content = SubElement(subtopic, 'SubTopicContent')
            subtopic_content.text = subtopic_info['content']

            # Add img tag for the subtopic if it exists
            if "img" in subtopic_info:
                for img_path in subtopic_info["img"]:
                    img_element = SubElement(subtopic, 'img')
                    img_element.text = img_path

    return tostring(chapter).decode()

# from xml.etree.ElementTree import Element, SubElement, tostring


# from xml.etree.ElementTree import Element, SubElement, tostring


def generate_xml_structure(data):
    slides = Element('Slides')

    # Add your predefined slides here (e.g., Slide1, Slide2, Slide3)
    slide_name = 'Slide1'
    slide = SubElement(slides, slide_name)

    SubElement(slide, 'Slide_Name').text = "Topics"
    j = 1
    for topic_key in data.keys():
        SubElement(slide, f'Topic_{j}').text = topic_key
        j += 1

    slide_counter = 2
    for topic_key, topic_value in data.items():
        subtopics = topic_value['Subtopics']

        if not subtopics:
            slide_name = f'Slide{slide_counter}'
            slide = SubElement(slides, slide_name)

            SubElement(slide, 'Slide_Name').text = "Topic_Summary"
            SubElement(slide, 'Topic_Name').text = topic_key
            SubElement(slide, 'Topic_Summary').text = topic_value['Topic_Summary'].strip()
            SubElement(slide, 'VoiceOver').text = topic_value['VoiceOver'].strip()

            slide_counter += 1
        else:
            for i, subtopic in enumerate(subtopics, start=1):
                slide_name = f'Slide{slide_counter}'
                slide = SubElement(slides, slide_name)

                SubElement(slide, 'Slide_Name').text = "Subtopic"
                # SubElement(slide, 'Topic_Name').text = topic_key
                stopic = SubElement(slide, 'Subtopic')
                stopic.text = subtopic['Subtopic']

                # bullets = SubElement(slide, 'Bullets')
                for j, bullet in enumerate(subtopic['Bullets'], start=1):
                    SubElement(slide, f'Bullet_{j}').text = bullet

                SubElement(slide, 'VO_Script').text = subtopic['VoiceOver'].strip()

                slide_counter += 1

    # Add your predefined slides at the end (e.g., Slide7)

    # xml_string =
    return tostring(slides).decode()


def process_pdf(uploaded_file):
    loader = PDFReader()
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        documents = loader.load_data(file=Path(temp_file.name))
    
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=1900))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    
    if "index" not in st.session_state:
        index = GPTVectorStoreIndex.from_documents(documents,service_context=service_context)
        index = index.as_query_engine()
        st.session_state.index = index
    # st.session_state.index = index
    return st.session_state.index
        

######################       defining tabs      ##########################################

# upload_col, refine_toc,  extract_col, miss_col, edit_col,voice_col, xml_col, manage_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__","⚪ __missing_Contents__", "⚪ __Edit Contents__", "⚪ Voice Over__", "⚪ __Export Generated XML__", "⚪ __Manage XMLs__"])
upload_col, refine_toc,  extract_col, voice_col, xml_col = st.tabs(["⚪ __Upload Chapter__","⚪ __Refine_TOC__", "⚪ __Extract_Contents__", "⚪ __Voice Over__", "⚪ __Export Generated XML__"])

if "toc" not in st.session_state:
    st.session_state.toc = {}



######################       Upload chapter column      ##########################################

uploaded_file = upload_col.file_uploader("Upload a Chapter as a PDF file", type="pdf")
toc_option = upload_col.radio("Choose a method to provide TOC", ("Generate TOC", "Copy Paste TOC"))
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
        clear_all_json_files()

        # index = 
        if "index" not in st.session_state:
            st.session_state.index = process_pdf(uploaded_file)

        upload_col.success("Index created successfully")
        clear_images_folder()
        clear_pages_folder()
    # read PDF file
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # display PDF file
        with fitz.open(uploaded_file.name) as doc:
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save("pages/page-%i.png" % page.number) 
            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)
                for image_index, img in enumerate(page.get_images(), start=1):
                

                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image = Image.open(io.BytesIO(image_bytes))
                    image_filename = f"images/image_page{page_index}_{image_index}.{image_ext}"
                    image.save(image_filename)

if toc_option == "Generate TOC":
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

    except (KeyError, AttributeError) as e:
        print("Error generating TOC")
        print(f"Error: {type(e).__name__} - {e}")


elif toc_option == "Copy Paste TOC":
    toc_input = upload_col.text_area("Paste your Table of contents:")

    if upload_col.button("Save TOC"):
        try:
            # table_of_contents = json.loads(toc_input)
            toc_res = f"convert the following table of contents into the specified JSON format\n"+ "Table of contents:\n"+ str(toc_input) + "\n JSON format:\n"+ str(forma)
            str_toc = call_openai(toc_res)
            table_of_contents = json.loads(str_toc)

            upload_col.write(table_of_contents)

            # if "table_of_contents" not in st.session_state:
            st.session_state.table_of_contents = table_of_contents
            upload_col.write(st.session_state.table_of_contents)

            upload_col.success("TOC loaded, Go to the next tab")

        except json.JSONDecodeError as e:
            upload_col.error("Invalid JSON format. Please check your input.")




######################       refining toc start      ##########################################


try:
    with refine_toc:
        column1, column2 = st.columns(2, gap="large")
        data = st.session_state.table_of_contents
        topic_data = {list(t.keys())[0]: list(t.values())[0] for t in data["Topics"]}
        if "topic_data" not in st.session_state:
            st.session_state['topic_data'] = topic_data
        column1.write("# Editor")

        column1.write("### Topics:")
        topic_name = column1.text_input("Enter New topic name:")

        if column1.button("Save New Topic"):
            if topic_name not in st.session_state['topic_data']:
                st.session_state['topic_data'][topic_name] = []
                update_json(topic_data)

        topic_options = list(st.session_state['topic_data'].keys())
        selected_topic = column1.selectbox("Select a Topic to edit Subtopics", topic_options)
        
        delete_topic = column1.button("Remove Selected Topic")
        if delete_topic:
            if selected_topic in st.session_state['topic_data']:
                del st.session_state['topic_data'][selected_topic]
                update_json(st.session_state['topic_data'])
                st.experimental_rerun()
                
                
        subtopics = st.session_state['topic_data'][selected_topic]

        column1.write("### Subtopics:")
        subtopics_input = column1.multiselect("Remove Unwanted Subtopics", subtopics, default=subtopics)

        if subtopics_input:
            st.session_state['topic_data'][selected_topic] = subtopics_input
            update_json(st.session_state['topic_data'])
        add = column1.button("Create New Subtopic")
        if "add" in st.session_state  or add:
            st.session_state['add'] = True
            new_subtopic = column1.text_input("Enter New Subtopic name:")
            if column1.button("Save New Subtopic"):
                if new_subtopic not in st.session_state['topic_data'][selected_topic]:
                    st.session_state['topic_data'][selected_topic].append(new_subtopic)
                    add= None
                    st.session_state['add'] = False
                    st.experimental_rerun()
        
        if column1.button("Save"):
            try:
                if "new_dict" not in st.session_state:
                        st.session_state.new_dict = {}
                for topic in st.session_state.toc["Topics"]:
                    for key, value in topic.items():
                        # Add a description for the topic
                        st.session_state.new_dict[key] = {'content': '', 'Subtopics': []}
                        # Add descriptions for the values
                        for item in value:
                            st.session_state.new_dict[key]['Subtopics'].append({'content': '', 'Subtopic': item})
            except (KeyError, AttributeError) as e:
                print("Error Formating TOC "+str(e))
                print(f"Error: {type(e).__name__} - {e}")

        column2.write("# Table of Contents")

        for topic, subtopics in st.session_state['topic_data'].items():
            column2.markdown(f"**{topic}**")
            for subtopic in subtopics:
                column2.write(f"- {subtopic}")




except (KeyError, AttributeError) as e:
    print("Error refining toc")
    print(f"Error: {type(e).__name__} - {e}")





######################       extract content      ##########################################



try:
    pagecol, ecol = extract_col.columns([2,5],gap="large")

    pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    selected_page = pagecol.number_input("Change page number to compare:",step=1)
    selected_image = f"page-{selected_page}.png"
    # Display the selected image
    if selected_image:
        pagecol.image(os.path.join("pages", selected_image), use_column_width=True)
    else:
        pagecol.warning("No images found in the 'pages' folder.")

    

    course_name = ecol.text_input("Enter course name")

    saved_extracts = [file for file in os.listdir('.') if file.endswith('.json')]

    # course_names = list(set([item['course_name'] for item in data]))
    selected_course = ecol.selectbox('Select a course name', saved_extracts)
    delete_button = ecol.button("Delete")

    # if a course name is selected, update new_dict with the corresponding data
    if selected_course:
        selected_course_path = os.path.join('.', selected_course)
        with open(selected_course_path, 'r') as json_file:
            data = json.load(json_file)
            st.session_state.new_dict = data['data']
            # st.write(data)


    if delete_button:
        selected_course_path = os.path.join('.', selected_course)
        os.remove(selected_course_path)
        print("Selected file path:", selected_course_path)

    # Delete the selected file
        try:
            os.remove(selected_course_path)
            st.success("File deleted successfully.")
        except OSError as e:
            st.error(f"Error deleting file: {e}")
        pass
    quer = ecol.button("Extract Contents")

    # seca, secb = extract_col.columns(2)
    if quer:
        progress_bar = ecol.progress(0)
        total_items = sum(len(subtopics_dict['Subtopics']) for _, subtopics_dict in st.session_state.new_dict.items()) + len(st.session_state.new_dict)
        items_processed = 0
        for topic, subtopics_dict in st.session_state.new_dict.items():
            for subtopic_dict in subtopics_dict['Subtopics']:
                subtopic_name = subtopic_dict['Subtopic']
                subtopicres = st.session_state.index.query("extract all the information under the subtopic  "+str(subtopic_name)+ ", in 4 paragraphs where each paragraph has minimum 40 words.")
                subtopic_dict['content'] = subtopicres.response
                items_processed += 1
                progress_bar.progress(items_processed / total_items)
                ecol.info(f"Extracted {subtopic_name}")
            
            topicres = st.session_state.index.query("extract the contents belonging to following topic into a paragraph :"+str(topic))
            subtopics_dict['content'] = topicres.response
            items_processed += 1
            progress_bar.progress(items_processed / total_items)
            
    with open(f'{course_name}.json', 'w') as outfile:

        json.dump({
                    'course_name': course_name,
                    'data': st.session_state.new_dict
                }, outfile)



    st.session_state.new_dict = data['data']
    for topic_key, topic_value in st.session_state.new_dict.items():
        expander = ecol.expander(f"{topic_key}")
        expander.write(topic_value["content"])
        for subtopic in topic_value["Subtopics"]:
            expander.markdown(f"**{subtopic['Subtopic']}**")
            expander.write(subtopic["content"])
                    
        
    
        

except (KeyError, FileNotFoundError,AttributeError) as e:
    print("Error Extracting Data")
    print(f"Error: {type(e).__name__} - {e}")


######################       voice over      ##########################################




try:
    edcol, excol = voice_col.columns([1,3])

    # Course Description
    course_description_limit = edcol.number_input("Course Description Word Count Limit", value=30, min_value=1)

    # Course Description VoiceOver
    course_description_voiceover_limit = edcol.number_input("Course Description VoiceOver Word Count Limit", value=50, min_value=1)

    # Topic Summary
    topic_summary_limit = edcol.number_input("Topic Summary Word Count Limit", value=30, min_value=1)

    # Topic Summary VoiceOver
    topic_summary_voiceover_limit = edcol.number_input("Topic Summary VoiceOver Word Count Limit", value=50, min_value=1)

    # Number of Bullets per Slide
    num_bullets_per_slide = edcol.number_input("Number of Bullets per Slide", value=4, min_value=1)

    # Number of Words per Bullet
    num_words_bullet = edcol.number_input("Number of Words per Bullet", value=20, min_value=1)

    # Bullet VoiceOver
    bullet_voiceover_limit = edcol.number_input("Bullet VoiceOver Word Count Limit", value=50, min_value=1)

    # Paraphrasing Percentage Range
    paraphrasing_range = edcol.slider("Paraphrasing % Range", min_value=25, max_value=35, value=(25, 35))

    coursename = excol.text_input("Enter Course Name")
    ex = excol.button("Generate Voice Over")
    # voice_col.write(st.session_state.new_dict)
    if ex:
        for topic_key, topic_value in st.session_state.new_dict.items():
            # Add "VoiceOver" key to the main topic
            topic = st.session_state.new_dict[topic_key]
            topic_content = topic['content']
            topic_voiceover_prompt = f"generate a voice over for the following paragraph in {topic_summary_voiceover_limit} words: {topic_content}"
            st.session_state.new_dict[topic_key]["VoiceOver"] = str(call_openai(topic_voiceover_prompt))
            
            topic_summary_prompt = f"generate a voice over for the following paragraph in {topic_summary_limit} words: {topic_content}"
            st.session_state.new_dict[topic_key]["Topic_Summary"] = str(call_openai(topic_summary_prompt))
            
            # Check if the topic has subtopics
            # if "Subtopics" in topic_value:
                # Iterate through the subtopics
            for subtopic in topic_value["Subtopics"]:
                subtopic_content = subtopic['content']
                subtopic_bullet_prompt = f"generate {num_bullets_per_slide} number of bullet points with {num_words_bullet} number of words per bullet from the following content: {subtopic_content}\n, give the output as a json list."
                bullets = call_openai(subtopic_bullet_prompt)
                listbul = ast.literal_eval(bullets.strip())
                subtopic['Bullets'] = listbul
                subtopic_voiceover_prompt = f"generate a voice over for the following content in {bullet_voiceover_limit} words: {subtopic_content}"
                subtopic["VoiceOver"] = str(call_openai(subtopic_voiceover_prompt))
               
        # excol.write(st.session_state.new_dict)
    if excol.button("generate xml"):

        xml_output = generate_xml_structure(st.session_state.new_dict)
        pretty_xml = minidom.parseString(xml_output).toprettyxml()
        excol.code(pretty_xml)
        voice_col.write(st.session_state.new_dict)


    

except (KeyError,NameError, FileNotFoundError,AttributeError) as e:
    print("Error Extracting Data")
    print(f"Error: {type(e).__name__} - {e}")








######################       export generated xml      ##########################################


try:
    # with 
    ondu, naduvan, rendu   = xml_col.columns([4,3,4],gap="large")

    ondu.write("### Select Images")
    ondu.write("")
    ondu.write("")

    left, right = ondu.columns(2)
    image_topic = left.selectbox("Select a topic", list(st.session_state.new_dict.keys()),label_visibility="collapsed")
    add_to_topic = right.button("Add Image to Topic")

# Dropdown menu for selecting a subtopic based on the selected topic
    image_subtopic = left.selectbox("Select a subtopic", [subtopic["Subtopic"] for subtopic in st.session_state.new_dict[image_topic]["Subtopics"]],label_visibility="collapsed")
    add_to_subtopic = right.button("Add image to Subtopic")

    image_files = [f for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    selected_images = []
    # for image in image_files:
    expander = ondu.expander("Select images")
    n_pages = 20

    image_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    page_index = ondu.number_input("Enter page number", min_value=1, max_value=n_pages, value=1)

    with ondu.expander(f"Page {page_index}", expanded=True):
        image_files = [f for f in os.listdir("images") if f.startswith(f'image_page{page_index}_') and f.endswith(tuple(image_exts))]
        # if image_files:
        for image_filename in image_files:
            file_path = os.path.join("images", image_filename)
            if os.path.isfile(file_path):
                ondu.image(file_path, caption=os.path.basename(file_path),width=150)
            else:
                st.warning(f"Image not found: {os.path.basename(file_path)}")
        # else:
        #     st.warning("No images found for this page.")
    
    selected_image = image_filename

    if add_to_topic:
        if "img" not in st.session_state.new_dict[image_topic]:
            st.session_state.new_dict[image_topic]["img"] = []
        st.session_state.new_dict[image_topic]["img"].append(selected_image)
        ondu.success(f"Image {selected_image} added to topic {image_topic}")

    if add_to_subtopic:
        for subtopic in st.session_state.new_dict[image_topic]["Subtopics"]:
            if subtopic["Subtopic"] == image_subtopic:
                if "img" not in subtopic:
                    subtopic["img"] = []
                subtopic["img"].append(selected_image)
                ondu.success(f"Image {selected_image} added to subtopic {image_subtopic}")
                break

    naduvan.write("### Compare ")
    pages_files = [f for f in os.listdir("pages") if f.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    # if pages_files:
    selected_page = naduvan.number_input("Compare Images",step=1)
    selected_image = f"page-{selected_page}.png"
    # Display the selected image
    if selected_image:
        naduvan.image(os.path.join("pages", selected_image), use_column_width=True)
    else:
        naduvan.warning("No images found in the 'pages' folder.")




    rendu.write("### Configure ")
    save_xml = rendu.button("Save XML")
    


    if save_xml:

        xml_output = json_to_xml(st.session_state.new_dict, chapter_name, NoOfWordsForVOPerBullet, NoOfWordsPerBullet, NoOfBullets) 
        pretty_xml = minidom.parseString(xml_output).toprettyxml()

        xml_file_path = os.path.join("images", f"{chapter_name}.xml")
        with open(xml_file_path, "w") as xml_file:
            xml_file.write(pretty_xml)
        # rendu.success(f"XML file saved as {xml_file_path}")

        with xml_col.expander("XML content"):
            xml_col.code(pretty_xml)

        # Zip the entire "images" folder with its contents
        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))

        zip_file_path = f"images/{chapter_name}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir("images", zipf)
        rendu.success(f"Zipped folder saved as {zip_file_path}")


 
                
except (KeyError,NameError, AttributeError) as e:
    print("Error saving XML")
    print(f"Error: {type(e).__name__} - {e}")



