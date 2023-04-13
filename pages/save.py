import streamlit as st
import json

# Load the JSON as a dictionary
json_dict = json.loads('''{
  "Funding the Balance Sheet": {
    "content": "",
    "Subtopics": [
      {
        "content": "",
        "Subtopic": "Cash Reserve Ratio (CRR)"
      },
      {
        "content": "",
        "Subtopic": "Liabilities not to be included for DTL/NDTL computation"
      },
      {
        "content": "",
        "Subtopic": "Exempted Categories"
      },
      {
        "content": "",
        "Subtopic": "Demand Liabilities"
      },
      {
        "content": "",
        "Subtopic": "Time Liabilities"
      },
      {
        "content": "",
        "Subtopic": "Other Demand and Time Liabilities"
      },
      {
        "content": "",
        "Subtopic": "Assets with the Banking System"
      },
      {
        "content": "",
        "Subtopic": "Borrowings from abroad by banks in India"
      },
      {
        "content": "",
        "Subtopic": "Arrangements with Correspondent Banks for Remittance Facilities"
      },
      {
        "content": "",
        "Subtopic": "Cost of CRR Maintenance"
      },
      {
        "content": "",
        "Subtopic": "Penalties for CRR Shortfall"
      }
    ]
  },
  "Clearing Corporation of India Limited (CCIL)": {
    "content": "",
    "Subtopics": [
      {
        "content": "",
        "Subtopic": "Netting/Elimination of Exposures"
      },
      {
        "content": "",
        "Subtopic": "Network"
      },
      {
        "content": "",
        "Subtopic": "Delivery Versus Payment III (DVP III) Settlement for Securities"
      },
      {
        "content": "",
        "Subtopic": "Real Time Gross Settlement (RTGS)"
      },
      {
        "content": "",
        "Subtopic": "Indian Financial Network"
      },
      {
        "content": "",
        "Subtopic": "Structured Financial Messaging System (SFMS)"
      },
      {
        "content": "",
        "Subtopic": "Public Key Infrastructure (PKI)"
      }
    ]
  },
  "Statutory Liquidity Ratio (SLR)": {
    "content": "",
    "Subtopics": [
      {
        "content": "",
        "Subtopic": "Maintenance of SLR"
      },
      {
        "content": "",
        "Subtopic": "Penalties for SLR Shortfall"
      }
    ]
  }
}''')

# Loop through each topic in the JSON dictionary
for topic, subtopics_dict in json_dict.items():
    # Get the content for the topic
    content = subtopics_dict['content']
    # Create a text input field for the content and store the updated content in the dictionary
    subtopics_dict['content'] = st.text_input(f"Enter content for {topic}:", value=content)
    # Loop through each subtopic for the topic
    for subtopic_dict in subtopics_dict['Subtopics']:
        subtopic_name = subtopic_dict['Subtopic']
        # Get the content for the subtopic
        content = subtopic_dict['content']
        # Create a text input field for the content and store the updated content in the dictionary
        subtopic_dict['content'] = st.text_input(f"Enter content for {subtopic_name} under {topic} topic:", value=content)

# Create a "Save" button
if st.button("Save"):
    # Convert the updated dictionary to JSON
    updated_json = json.dumps(json_dict, indent=2)
    # Write the updated JSON to a file or database, or print it to the console
    st.write(json_dict)
