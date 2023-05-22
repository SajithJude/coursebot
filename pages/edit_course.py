import streamlit as st
import json
import os
        
with open(f"output/{st.session_state.selected_pptx}", "r") as f:
    json_data = json.load(f)
    st.json(json_data)

