import streamlit as st
import os
import shutil
import base64
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.buy_me_a_coffee import button
from streamlit_elements import elements, mui, html

import json 
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load your logo image and convert it to base64s
hide_menu_style = """
        <style>
        #MainMenu {display:none;}
        [data-testid="stHeader"]>header {{
        display:none !important;
        }}
        .css-hqnn1b{display:none !important;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_image_base64(image_file):
    with open(image_file, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Replace with the path to your logo image
logo_image = "flipick_coursebot.png"
logo_base64 = get_image_base64(logo_image)

# Define your header with the logo and home button

def custom_header(logo_base64):
    header = f'''
    <style>
        .header {{
            height:130px;
            background-color:white;
            display:flex;
            align-items:center;
            padding:0px 20px;
            position:fixed;
            top:-40px;
            left:0;
            right:0;
            z-index:1000;
        }}
    </style>
    <div class="header">
        <div style="display:flex;align-items:center;">
            <img src="data:image/png;base64,{logo_base64}" style="margin-top:40px; margin-left:50px; max-height: 100%; object-fit: contain; margin-right:15px;"/>
        </div>
        <div style="display:flex;align-items:center;margin-left:auto; top: 50%;">
            <a href="/" style="text-decoration:none; padding-top:40px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="100" viewBox="0 0 24 24" fill="none" stroke="#2953B3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-home">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
            </a>
        </div>
    </div>
    '''
    return header

# Display the custom header in the Streamlit app
st.markdown(custom_header(logo_base64), unsafe_allow_html=True)
# st.write('<style>div.stDivider.horizontal{height:1px;margin:25px 0;}</style>', unsafe_allow_html=True)


# Create a directory to store uploaded PPTX files
upload_directory = "data"
os.makedirs(upload_directory, exist_ok=True)


if st.session_state.passed_ARG:
    json_file_path = f"output/{st.session_state.passed_ARG}"
    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)
    # st.write(json_data)
    # st.session_state.
    st.session_state.CourseStructure = json_data



name_vid =st.text_input("Name of video")

if st.button("Create Video"):

    headers = {
                    'Authorization': "5ad72dcaafb054f6c163e2feb9334539",
                    'Content-Type': 'application/json'
                }

                # Define the data for the API request
    api_data = {
    "title":name_vid,
    "description": "First part with lo cn cd and top 1",
    "visibility": "public",
    "templateId": "1419387f-2154-4fff-a7f1-b2d6c9c2fca8",
   "templateData": {
        "course_name": st.session_state.CourseStructure["Scenes"][0]["Scene1"]["Title"],
        "course_description": st.session_state.CourseStructure["Scenes"][0]["Scene1"]["TextOverlay"],
        "intovo": st.session_state.CourseStructure["Scenes"][0]["Scene1"]["Voiceover"],

        "subtopic_2": st.session_state.CourseStructure["Scenes"][0]["Scene2"]["Title"],
        "copy_2": st.session_state.CourseStructure["Scenes"][0]["Scene2"]["TextOverlay"],
        "script2": st.session_state.CourseStructure["Scenes"][0]["Scene2"]["Voiceover"],

        "subtopic_3": st.session_state.CourseStructure["Scenes"][0]["Scene3"]["Title"],
        "copy_3": st.session_state.CourseStructure["Scenes"][0]["Scene3"]["TextOverlay"],
        "script3": st.session_state.CourseStructure["Scenes"][0]["Scene3"]["Voiceover"],

        # Continue with this pattern for remaining scenes
        "subtopic_4": st.session_state.CourseStructure["Scenes"][0]["Scene4"]["Title"],
        "copy_4": st.session_state.CourseStructure["Scenes"][0]["Scene4"]["TextOverlay"],
        "script4": st.session_state.CourseStructure["Scenes"][0]["Scene4"]["Voiceover"],

        "subtopic_5": st.session_state.CourseStructure["Scenes"][0]["Scene5"]["Title"],
        "copy_5": st.session_state.CourseStructure["Scenes"][0]["Scene5"]["TextOverlay"],
        "script5": st.session_state.CourseStructure["Scenes"][0]["Scene5"]["Voiceover"],

        # ... and so on, for all scenes in your structure.
    },
    "test": True,
    "callbackId": "john@example.com"
}

    # with tab_synthesia.expander("api_data"):
    #     st.write(api_data)

    # Make the API request
    response = requests.post('https://api.synthesia.io/v2/videos/fromTemplate', headers=headers, data=json.dumps(api_data))
    if response.status_code == 201:
        st.info('Sample scene video creation process started successfully.')
        video_id = response.json()['id']
        st.write(f'Video ID for Sample scene: {video_id}')
        st.code(video_id)
        if "video_id" not in st.session_state:
            st.session_state.video_id = video_id

        editURL = f"https://app.synthesia.io/#/video-edit/{video_id}"


        url = f"https://share.synthesia.io/embeds/videos/{video_id}"
        st.write("Edit Video Link")
        
        st.write(editURL)
        iframe_html = f""" <div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src="{url}" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"""
        components.html(iframe_html,height=600)
        # frame = f"<div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src=" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"



    else:
        st.write('An error occurred during the video creation process for Sample scene.')
        st.write(f'Response status code: {response.status_code}')
        st.write(f'Response content: {response.content}')

