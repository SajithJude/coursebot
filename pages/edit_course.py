# from venv import create
# from regex import X
import streamlit as st
import json
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components

import requests

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
        
with open(f"output/{st.session_state.selected_pptx}", "r") as f:
    json_data = json.load(f)
    if "dictionary" not in st.session_state:
        st.session_state.dictionary = json_data
        #st.json(json_data)


tab_xml, tab_synthesia = st.tabs(["Split Templates","Synthesia"])



############ XML tab ###############



if tab_xml.button("Show XML"):
    # st.session_state.dictionary

    template1 = {
        "Course": st.session_state.dictionary["Course"],
        "Topics": [st.session_state.dictionary["Topics"][0]],
        "Course_Objectives": st.session_state.dictionary["Course_Objectives"]
    }

    if "template1" not in st.session_state:
        st.session_state.template1 = template1

    other_templates = []
    for i in range(1, len(st.session_state.dictionary["Topics"])):
        other_template= {
            # "Course": st.session_state.dictionary["Course"],
            "Topics": [st.session_state.dictionary["Topics"][i]],
            # "Course_Objectives": st.session_state.dictionary["Course_Objectives"]
        }
        if i != len(st.session_state.dictionary["Topics"]) - 1:
            other_templates.append(other_template)
        else:
            final_template = other_template

    # Adding congratulations message to the final template
    # final_template = other_templates[-1]
    final_template["Topics"][0]["Subtopics"].append({
        "Subtopic_Name": "Congratulations",
        "Message1": "Congratulations on completing the course! We hope you found the content valuable and gained new insights.",
        "VoiceOver": "Congratulations on completing the course! We hope you found the content valuable and gained new insights.",
        "Image": ""
    })

    # Printing the results
    st.write("Template 1:")
    st.write(st.session_state.template1)
    st.write("")

    st.write("Other Templates:")
    for i, template in enumerate(other_templates):
        st.write(f"Template {i+2}:")
        st.write(template)
        st.write("")

    st.write("Final Template:")
    st.write(final_template)
        
    # xml = create_xml(st.session_state.dictionary)
    # pretty_xml = minidom.parseString(xml).toprettyxml()
    

    # tab_xml.code(pretty_xml)
    # save_dictionary_as_json()






if tab_synthesia.button("Template 1"):

    headers = {
                    'Authorization': "5ad72dcaafb054f6c163e2feb9334539",
                    'Content-Type': 'application/json'
                }

                # Define the data for the API request
    api_data = {
        "title": "CB Template-1",
        "description": "First part with lo cn cd and top 1",
        "visibility": "public",
        "templateId": "fa673de8-f4c5-413c-9e43-39ff7cdc1937",
       "templateData": {
            "Course_Name": st.session_state.template1["Course"]["Course_Name"],
            "Course_Description": st.session_state.template1["Course"]["Course_Description"],

            "objectives_1": st.session_state.template1["Course_Objectives"][0]["Objective"],
            "lo_voiceover": st.session_state.template1["Course_Objectives"][0]["VoiceOver"],

            "objectives_2": "", # Please replace it with the real data if exists
            "objectives_3": "", # Please replace it with the real data if exists
            "objectives_4": "", # Please replace it with the real data if exists
            "objectives_5": "", # Please replace it with the real data if exists

            "Topic_Name": st.session_state.template1["Topics"][0]["Topic_Name"],
           
            "SubTopic_1": st.session_state.template1["Topics"][0]["Subtopics"][0]["Subtopic_Name"],
            "Copy_1": st.session_state.template1["Topics"][0]["Subtopics"][0]["Bullets"],
            "copy_1_vo":st.session_state.template1["Topics"][0]["Subtopics"][0]["VoiceOver"],

            "SubTopic_2": st.session_state.template1["Topics"][0]["Subtopics"][1]["Subtopic_Name"] ,
            "Copy_2": st.session_state.template1["Topics"][0]["Subtopics"][1]["Bullets"] ,
            "copy_2_vo":st.session_state.template1["Topics"][0]["Subtopics"][1]["VoiceOver"],

            # Continue with this pattern for remaining Subtopics and Copy fields
            "SubTopic_3": st.session_state.template1["Topics"][0]["Subtopics"][2]["Subtopic_Name"] ,
            "Copy_3": st.session_state.template1["Topics"][0]["Subtopics"][2]["Bullets"] ,
            "copy_3_vo":st.session_state.template1["Topics"][0]["Subtopics"][2]["VoiceOver"],

            
            # "SubTopic_4": st.session_state.template1["Topics"][0]["Subtopics"][3]["Subtopic_Name"] ,
            # "Copy_4": st.session_state.template1["Topics"][0]["Subtopics"][3]["Bullets"] ,
            # "copy_4_vo":st.session_state.template1["Topics"][0]["Subtopics"][3]["VoiceOver"],

            
            # "SubTopic_5": st.session_state.template1["Topics"][0]["Subtopics"][4]["Subtopic_Name"] ,
            # "Copy_5": st.session_state.template1["Topics"][0]["Subtopics"][4]["Bullets"] ,
            # "copy_5_vo":st.session_state.template1["Topics"][0]["Subtopics"][4]["VoiceOver"],


        },
        "test": True,
        "callbackId": "john@example.com"
    }

    tab_synthesia.write(api_data)

    # Make the API request
    response = requests.post('https://api.synthesia.io/v2/videos/fromTemplate', headers=headers, data=json.dumps(api_data))
    if response.status_code == 201:
        tab_synthesia.info('Sample scene video creation process started successfully.')
        video_id = response.json()['id']
        tab_synthesia.write(f'Video ID for Sample scene: {video_id}')
        tab_synthesia.code(video_id)
        url = f"https://share.synthesia.io/embeds/videos/{video_id}"
        tab_synthesia.write(url)
        iframe_html = f""" <div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src="{url}" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"""
        components.html(iframe_html,height=600)
        # frame = f"<div style="position: relative; overflow: hidden; padding-top: 56.25%;"><iframe src=" loading="lazy" title="Synthesia video player - CB Template-1" allow="encrypted-media; fullscreen;" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0; border: none; padding: 0; margin: 0; overflow:hidden;"></iframe></div>"



    else:
        tab_synthesia.write('An error occurred during the video creation process for Sample scene.')
        tab_synthesia.write(f'Response status code: {response.status_code}')
        tab_synthesia.write(f'Response content: {response.content}')





# xml = create_xml(json_data)
# pretty_xml = minidom.parseString(xml).toprettyxml()
    

# tab_xml.code(pretty_xml)


############ Synthesia tab ###############


# data = json_data
# api_token = tab_synthesia.text_input('Enter your Synthesia API token')
# template_id = tab_synthesia.text_input('Enter your Synthesia template ID')

# exp = st.expander("Input data")

# # with tab_synthesia.expander("Input Data"):
# exp.write(data["Course"]["Course_Name"])
# exp.write(data["Course"]["Course_Description"])
# exp.write(data["Course"]["VoiceOver"])



# # Button to start topic slide video creation process
# if tab_synthesia.button('Create Topic Slide Video'):
#     tab_synthesia.write('Starting topic slide video creation process...')
    
#     # Define the headers for the API request
#     headers = {
#         'Authorization': api_token,
#          'Content-Type': 'application/json'
#     }

#     # Define the data for the API request
#     api_data = {
#         "title": data["Course"]["Course_Name"],
#         "description": data["Course"]["Course_Name"],
#         "visibility": "public",
#         "templateId": template_id,
#         "templateData": {
#             "script": data["Course"]["VoiceOver"],
#             "Course_Name": data["Course"]["Course_Name"],
#             "Course_Description": data["Course"]["Course_Description"],
#         },
#         "test": False,
#         "callbackId": "john@example.com"
#     }
        
#     # Make the API request
#     response = requests.post('https://api.synthesia.io/v2/videos/fromTemplate', headers=headers, data=json.dumps(api_data))
        
#     # Handle the response
#     if response.status_code == 200:
#         tab_synthesia.write('Topic slide video creation process started successfully.')
#         video_id = response.json()['id']
#         tab_synthesia.write(f'Video ID for Topic Slide: {video_id}')
#     else:
#         tab_synthesia.write('An error occurred during the video creation process for Topic Slide.')
#         tab_synthesia.write(f'Response status code: {response.status_code}')
#         tab_synthesia.write(f'Response content: {response.content}')


# video_id = st.text_input('Enter the Video ID to check its status')

# if st.button('Check Video Creation Status'):
#     st.write('Checking video creation status...')

#     # User input for Video ID

#     # Define the headers for the API request
#     headers = {
#         'Authorization': api_token,
#         'Content-Type': 'application/json'
#     }

#     # Make the API request
#     response = requests.get(f'https://api.synthesia.io/v2/videos/{video_id}', headers=headers)

#     # Handle the response
#     if response.status_code == 200:
#         video_data = response.json()
#         st.info(f'Video ID: {video_data["id"]}')
#         st.info(f'Video Title: {video_data["title"]}')
#         st.info(f'Video Description: {video_data["description"]}')
#         st.info(f'Video Status: {video_data["status"]}')
#     else:
#         st.error('An error occurred during the video status check.')
#         st.error(f'Response status code: {response.status_code}')
#         st.error(f'Response content: {response.content}')