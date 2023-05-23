from venv import create
from regex import X
import streamlit as st
import json
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

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
    st.json(json_data)

xml = create_xml(json_data)
pretty_xml = minidom.parseString(xml).toprettyxml()
    

st.code(pretty_xml)