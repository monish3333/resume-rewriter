import streamlit as st
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import json

# Set page config
st.set_page_config(
    page_title="AI Resume Rewriter", 
    layout="wide",
    page_icon="✨"
)

# Title and description
st.title("✨ AI Resume Rewriter")
st.write("Upload your resume for instant AI-powered improvements")

# File upload with size limit (3MB)
uploaded_file = st.file_uploader(
    "Choose a PDF file (max 3 pages)", 
    type="pdf",
    accept_multiple_files=False
)

job_role = st.text_input("Target Job Title (Optional)", placeholder="e.g., Software Engineer")

if uploaded_file:
    try:
        # Verify file size
        if uploaded_file.size > 3 * 1024 * 1024:  # 3MB limit
            st.error("File too large. Please upload a smaller file (max 3MB).")
            st.stop()

        # Extract text from PDF
        pdf = PdfReader(BytesIO(uploaded_file.read()))
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
        if not text.strip():
            st.error("Couldn't extract text from PDF. Please upload a text-based PDF.")
            st.stop()

        if st.button("✨ Enhance My Resume", type="primary"):
            with st.spinner("AI is analyzing your resume..."):
                # Call OpenRouter API with proper headers
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {st.secrets['OPENROUTER_KEY']}",
                        "HTTP-Referer": "https://resume-rewriter.streamlit.app",
                        "X-Title": "Resume Rewriter"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct",
                        "messages": [{
                            "role": "user",
                            "content": f"""Please improve this resume for a {job_role if job_role else 'general'} position. 
                            Keep the original content but enhance wording, formatting, and professionalism.
                            Return ONLY the improved resume text, no commentary.
                            Original resume:\n{text}"""
                        }],
                        "temperature": 0.3  # Less random output
                    },
                    timeout=30  # 30 second timeout
                )

                # Debug: Show raw response (comment out in production)
                # st.json(response.json())

                # Validate API response
                if response.status_code != 200:
                    error_msg = response.json().get("error", {}).get("message", "Unknown API error")
                    st.error(f"API Error: {error_msg}")
                    st.stop()

                data = response.json()
                if "choices" not in data or len(data["choices"]) == 0:
                    st.error("Unexpected API response format")
                    st.stop()

                improved_resume = data["choices"][0]["message"]["content"]
                
                # Display results
                st.success("✅ Resume enhanced successfully!")
                st.markdown("---")
                st.markdown(improved_resume)
                st.download_button(
                    "⬇️ Download Improved Resume",
                    improved_resume,
                    file_name=f"improved_resume_{job_role or 'general'}.txt",
                    mime="text/plain"
                )

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()
