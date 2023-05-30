import streamlit as st
import os
import shutil
import base64
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.buy_me_a_coffee import button
from streamlit_elements import elements, mui, html
# import streamlit.ReportThread as ReportThread

# from streamlit.report_thread import get_report_ctx

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
import streamlit as st

# Dictionary containing scene information
st.session_state.st.session_state.scene_data = {
    "CourseStructure": {
        "Scenes": [
            {
                "Scene1": {
                    "Title": "Add Title Here",
                    "TextOverlay": "Leave This Empty",
                    "Voiceover": "Leave This Empty"
                },
                "Scene2": {
                    "Title": "Add Title Here",
                    "TextOverlay": "Leave This Empty",
                    "Voiceover": "Leave This Empty"
                },
                "Scene3": {
                    "Title": "Add Title Here",
                    "TextOverlay": "Leave This Empty",
                    "Voiceover": "Leave This Empty"
                }
            }
        ]
    }
}

# Current scene index
if 'current_scene_index' not in st.session_state:
    st.session_state.current_scene_index = 0

# Function to update the scene based on index
def update_scene(index):
    scene = st.session_state.scene_data["CourseStructure"]["Scenes"][0]
    scene_name = f"Scene{index+1}"
    if scene_name in scene:
        return scene[scene_name]
    return None

# Previous button callback
def previous_button_callback():
    if st.session_state.current_scene_index > 0:
        st.session_state.current_scene_index -= 1
        update_app()

# Next button callback
def next_button_callback():
    scene_count = len(st.session_state.scene_data["CourseStructure"]["Scenes"][0])
    if st.session_state.current_scene_index < scene_count - 1:
        st.session_state.current_scene_index += 1
        update_app()

# Update the app based on the current scene index
def update_app():
    scene = update_scene(st.session_state.current_scene_index)
    st.container.empty()













col1, col2, col3 = st.columns(3)

# First column - Previous button and preview image
with col1:
    prev_button = st.button("Previous", on_click=previous_button_callback, key=f"prev{st.session_state.current_scene_index+4}")
    preview_image = st.image("https://images.wondershare.com/recoverit/2022recoverit-dr/tab-img01.png")

# Middle column - Tabs
with col2:
    tabs = st.tabs(["Scene Information"])
    if tabs[0]:
        # if scene:
        st.subheader(f"Scene {st.session_state.current_scene_index + 1}")
        scene["Title"] = st.text_input("Title", scene["Title"])
        scene["TextOverlay"] = st.text_input("Text Overlay", scene["TextOverlay"])
        scene["Voiceover"] = st.text_input("Voiceover", scene["Voiceover"])

# Third column - Next button and variable image display
with col3:
    next_button = st.button("Next", on_click=next_button_callback, key=f"nex{st.session_state.current_scene_index+4}")
    variable_image = st.image("https://images.wondershare.com/recoverit/2022recoverit-dr/tab-img01.png")

# Initial app setup
update_app()
