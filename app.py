import gspread
import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re
import time  # For API rate limits
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini API (Placeholder key)
genai.configure(api_key="AIzaSyA*******12345")

# Authenticate Google Sheets API (Placeholder filename)
gc = gspread.service_account(filename='sheetapi_98765.json')
wks = gc.open_by_key("1jYminN*******54321")
currentwks = wks.sheet1  # Select the first sheet

# Load transparent logo (Placeholder path)
logo_path = "logo2.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
else:
    logo = None

# Fixed Job Description (JD)
FIXED_JD = """We seek a technically rigorous AI Research engineer to advance our core AI systems, with a focus on training, fine-tuning, and optimizing large language models (LLMs). You will bridge cutting-edge research with production-grade engineering, designing high-performance implementations for GPU/TPU clusters and iterating on agentic workflows. This role demands fluency in both theoretical foundations (e.g., transformer architectures, optimization theory) and applied engineering to deploy scalable AI solutions."""

# Streamlit UI Styling
st.set_page_config(page_title="Shoppin Resume GPT", layout="centered", page_icon="✅")

# Centered Header with Logo
if logo:
    st.image(logo, width=200)

st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>Shoppin Resume GPT</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>A CV-shortlisting GPT for an AI Research Engineer</h3>", unsafe_allow_html=True)
st.write("---")

# Sidebar for uploading files
with st.sidebar:
    st.header("Upload Your Resume 📄")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# Function to generate Gemini AI response
def get_gemini_response(input):
    """Generate ATS analysis response using Gemini AI."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input)
        return response.text
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return None

# Function to extract text from a PDF
def input_pdf_text(uploaded_file):
    """Extract text from uploaded PDF."""
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Function to extract structured data from AI response
def extract_details(response_text):
    """Extract details from AI response in JSON format."""
    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())

            # Convert lists to comma-separated strings
            for key, value in response_json.items():
                if isinstance(value, list):
                    response_json[key] = ", ".join(value)
            
            # Ensure phone number is treated as a string and formatted correctly
            if "Phone Number" in response_json:
                phone_number = str(response_json["Phone Number"]).strip()
                response_json["Phone Number"] = f"'{phone_number}"  # Add leading apostrophe to avoid formula error

            return response_json
        else:
            st.error("Invalid JSON format in response.")
            return {}
    except Exception as e:
        st.error(f"Error extracting details: {e}")
        return {}

# Function to check if email exists in the spreadsheet
def email_exists(email):
    """Check if the email already exists in the spreadsheet."""
    email_column = currentwks.col_values(2)  # Assuming "Email" is in the second column
    return email in email_column

# Function to update Google Sheets without modifying column structure
def update_spreadsheet(candidate_data):
    """Update Google Sheet while keeping existing columns and avoiding duplicates."""
    try:
        existing_headers = currentwks.row_values(1)  # Get column headers
        email = candidate_data.get("Email", "").strip()

        if not email:
            st.error("No email found in extracted data. Skipping entry.")
            return
        
        if email_exists(email):
            st.warning(f"Candidate with email {email} already exists. Skipping entry.")
            return

        # Prepare row data in the order of existing headers
        candidate_row = [candidate_data.get(header, "") for header in existing_headers]

        st.write("Appending row:", candidate_row)
        currentwks.append_row(candidate_row, value_input_option='USER_ENTERED')

        time.sleep(2)
        st.success(f"✅ Candidate {candidate_data.get('Candidate Name', 'Unknown')} successfully added to the spreadsheet!")
    except Exception as e:
        st.error(f"Error updating Google Sheet: {e}")

# Job description section
st.subheader("📌 Job Description")
st.info(FIXED_JD)

# Submit button with progress bar
if st.button("Analyze Resume"):
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing Resume... Please wait"):
            text = input_pdf_text(uploaded_file)

            input_prompt = f"""
            Hey, act like an experienced ATS (Application Tracking System) with deep expertise in software engineering, 
            data science, and AI. Your task is to evaluate the resume based on the given job description.
            Provide a highly accurate percentage match and missing keywords.

            Extract the following details:
            - Candidate Name
            - Email
            - Phone Number
            - Skills
            - Experience
            - Education
            - Certifications
            - Current Job Title
            - Current Employer
            - Notice Period
            - Expected Salary
            - Location
            - LinkedIn Profile
            - Tech Fit Score (%)

            Resume: {text}
            Description: {FIXED_JD}

            Respond in JSON format:
            {{
                "Candidate Name": "", "Email": "", "Phone Number": "", "Skills": "", 
                "Experience": "", "Education": "", "Certifications": "", 
                "Current Job Title": "", "Current Employer": "", "Notice Period": "", 
                "Expected Salary": "", "Location": "", "LinkedIn Profile": "", "Tech Fit Score": "%"
            }}
            """

            response = get_gemini_response(input_prompt)
            if response:
                candidate_data = extract_details(response)
                st.success("✅ Resume analyzed successfully!")
                st.write(candidate_data)

                score = int(candidate_data.get("Tech Fit Score", "0").replace("%", "")) if candidate_data.get("Tech Fit Score") else 0

                if score > 50:
                    update_spreadsheet(candidate_data)
                else:
                    st.warning(f"⚠️ Score {score} is below 50, not adding to the spreadsheet.")
    else:
        st.error("⚠️ Please upload a resume first.")
