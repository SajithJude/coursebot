import streamlit as st
import os
import shutil
import base64
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.buy_me_a_coffee import button
from streamlit_elements import elements, mui, html


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



m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #5007D9;
    font-size:25px;border-radius:6px;
    font-color: #ffffff;
    color: #ffffff;
    box-shadow: 1px 1px 5px grey;
    margin-top:1px;
    min-width: 140px;
    border: solid #5007D9 1px;
}
</style>""", unsafe_allow_html=True)



st.write("")
col1, col2= st.columns((10,4))
with col1:
    st.write("")

with col2:
    create_new = st.button("### Create new Project",use_container_width=True)
    # create_new = st.button("### Create new Chapter")
    if create_new:
        switch_page("create_course")

st.write("")
#######  PPTX Table   ##########

saved_courses = [file for file in  os.listdir('./output') if file.endswith('.json')]
if "saved_courses" not in st.session_state:
    st.session_state.saved_courses = saved_courses

if "edit_video" not in st.session_state:
    st.session_state.edit_video = "false"

if "create_video" not in st.session_state:
    st.session_state.create_video = "false"

if "preview_video" not in st.session_state:
    st.session_state.preview_video = "false"

if "download_video" not in st.session_state:
    st.session_state.download_video = "false"



def create_video():
    st.session_state.create_video = "true"

def edit_video():
    st.session_state.edit_video = "true"

def preview_video():
    st.session_state.preview_video = "true"

def download_video():
    st.session_state.download_video = "true"



########## Table ###########
if "selected_json" not in st.session_state:
    st.session_state.selected_json = ''

colms = st.columns((4, 1, 1,1,1,1,1))

fields = ["Project Name", 'Status', '', '', 'Actions', '','' ]
for col, field_name in zip(colms, fields):
    # header
    col.write(f"##### {field_name}")
st.markdown("""
        <div style="background-color:#560AE8;height:1px;margin-top:2px;margin-bottom:10px;"></div>
    """, unsafe_allow_html=True)

i = 1
for Name in saved_courses:
    i += 1
    col1, col2, col5,col6 = st.columns((4, 1,1,4))

    col1.write(f"##### {Name}") 
    col2.write("Draft")
    with col5:
        edit_file = st.button("Edit Project", key=f"edit{Name}")
        if edit_file:
            switch_page("edit_course")  

    
        # with st.expander("Video Options"):
    j = 2
    z = 1
      
    for j in range(3):
        # with st.spinner("Loading..."):
        x = col5.expander(" Video")

        cola,  colb, colc, cold, cole = x.columns((5, 1,1,1,1))

        # with cola:
        #     st.write(f"###### {Name} Video part {j+1}")
        
        with colb:
            with elements(f"create_element{Name}{j+1}"):
                but = mui.Button(
                    mui.icon.SlideshowOutlined,
                    onClick  = create_video,
                    key=f"button_create{z+1}"
                )
                z+=1

        with colc:
            with elements(f"edit_element{Name}{j+1}"):
                mui.Button(
                    mui.icon.EditOutlined,
                    onClick  = edit_video,
                    key=f"button_edit{z+1}"
                )
                z+=1

        with cold:
            with elements(f"preview_element{Name}{j+1}"):
                mui.Button(
                    mui.icon.VisibilityOutlined,
                    onClick  = preview_video,
                    key=f"button_preview{z+1}"
                )
                z+=1
        
        with cole:
            with elements(f"download_element{Name}{j+1}"):
                mui.Button(
                    mui.icon.CloudDownloadTwoTone,
                    onClick  = download_video,
                    key=f"button_download{z}"
                )
                z+=1
        j += 1
        
        

            
    st.markdown("""
    <div style="background-color:#560AE8;height:1px;margin-top:5px;margin-bottom:5px;"></div>
""", unsafe_allow_html=True)
    
    
if st.session_state.create_video == "true":
     switch_page("create_video")

if st.session_state.edit_video == "true":
     switch_page("edit_video")

if st.session_state.preview_video == "true":
     switch_page("preview_video")

if st.session_state.download_video == "true":
     switch_page("download_video")
        


