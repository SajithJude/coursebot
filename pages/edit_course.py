import streamlit as st
import json
import os
        

extract_col, voice_col, xml_col = st.tabs([ "⚪ __Extract Contents__", "⚪ __XML__", "⚪ __Images__"])

with open(st.session_state.selected_pptx, "r") as f:
    json_data = json.load(f)
    st.json(json_data)

