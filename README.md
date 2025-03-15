# Resume-Scanner-
Resume GPT is a resume shortlisting tool built using Streamlit, Google Sheets API, and Gemini AI. It analyzes resumes for an AI Research Engineer position and updates shortlisted candidates in a Google Sheet.

# Features
1.Extracts text from uploaded PDF resumes. 

2.Analyzes resumes using Gemini AI.

3.Matches resumes against a fixed job description.

4.Calculates a tech fit score.

5.Prevents duplicate entries in Google Sheets.

6.Provides insights on missing keywords.

# Tech Stack
Python (Streamlit, gspread, google.generativeai, PyPDF2, dotenv, PIL), Google Sheets API (for storing shortlisted candidates), Gemini AI (for resume analysis)

# How It Works
1.Upload a PDF resume.

2.The resume is processed and analyzed against the job description.

3.Extracted details and a tech fit score are generated.

4.If the score is above 50%, the candidate is added to Google Sheets.

5.Prevents duplicate entries based on email.
