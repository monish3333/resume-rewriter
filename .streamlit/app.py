import streamlit as st
import requests
from PyPDF2 import PdfReader
from io import BytesIO

# Set page config
st.set_page_config(page_title="AI Resume Rewriter", layout="wide")

# Title
st.title("✨ AI Resume Rewriter")
st.write("Upload your resume for instant AI-powered improvements")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
job_role = st.text_input("Target Job Title (Optional)")

if uploaded_file:
    try:
        # Extract text from PDF
        pdf = PdfReader(BytesIO(uploaded_file.read()))
        text = "\n".join([page.extract_text() for page in pdf.pages])
        
        if st.button("Enhance My Resume"):
            with st.spinner("AI is working its magic..."):
                # Call OpenRouter API
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {st.secrets['OPENROUTER_KEY']}",
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct",
                        "messages": [{
                            "role": "user",
                            "content": f"Improve this resume for {job_role}:\n{text}"
                        }]
                    }
                )
                
                # Show result
                improved_resume = response.json()["choices"][0]["message"]["content"]
                st.success("Done! Here's your enhanced resume:")
                st.markdown(improved_resume)
                st.download_button(
                    "Download Improved Resume",
                    improved_resume,
                    file_name="improved_resume.txt"
                )
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
