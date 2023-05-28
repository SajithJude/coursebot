import streamlit as st
import os
import shutil
import base64
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.buy_me_a_coffee import button


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
    background-color: #FFFFFF;
    font-size:25px;border-radius:6px;
    box-shadow: 1px 1px 5px grey;
    margin-top:1px;
}
</style>""", unsafe_allow_html=True)



st.write("")
col1, col2= st.columns((10,2))
with col1:
    st.write("")

with col2:
    create_new = st.button("### Create new Chapter")
    if create_new:
        switch_page("create_course")

st.write("")


#######  PPTX Table   ##########

saved_courses = [file for file in  os.listdir('./output') if file.endswith('.json')]
if "saved_courses" not in st.session_state:
    st.session_state.saved_courses = saved_courses

def display_ppt():
    st.write("Show PPT")

def delete_file():
    st.write("Delete file")


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
    col1, col2, col3, col4, col5, col6, col7 = st.columns((4, 1, 1,1,1,1,1),gap="small")
    with col1:
        st.write(Name)
   
    with col2:
        st.write("Draft")

    with col3:
        edit_file = st.button("Edit Project", key=f"edit{Name}")
        if edit_file:
            switch_page("edit_project")  
    
    with col4:
        edit_file = st.button("Create Video", key=f"create{Name}")
        if edit_file:
            switch_page("create_video") 
    
    with col5:
        edit_file = st.button("Edit Video", key=f"edit_vid{Name}")
        if edit_file:
            switch_page("edit_video") 

    with col6:
        edit_file = st.button("Preview Video", key=f"prview{Name}")
        if edit_file:
            switch_page("preview_video") 

    with col7:
        edit_file = st.button("Download", key=f"download{Name}")
        if edit_file:
            switch_page("download_video") 
            
    st.markdown("""
    <div style="background-color:#560AE8;height:1px;margin-top:5px;margin-bottom:5px;"></div>
""", unsafe_allow_html=True)
        


