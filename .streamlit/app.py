import streamlit as st
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import json
import time

# Set page config
st.set_page_config(
    page_title="AI Resume Rewriter Pro", 
    layout="wide",
    page_icon="📄"
)

# Initialize session state
if 'last_upload' not in st.session_state:
    st.session_state.last_upload = None
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

# ===== ADDED: Key Verification Block =====
# Key Verification Block
st.write("🔑 Key being used:", st.secrets.get('OPENROUTER_KEY', 'NOT FOUND')[:4] + "...")
st.write("🌐 Referer URL:", st.secrets.get('APP_URL', 'Not set'))
# ===== END OF ADDED BLOCK =====

# Title and description
st.title("📄 AI Resume Rewriter Pro")
st.markdown("""
<style>
    .stDownloadButton button {
        background-color: #4CAF50 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.write("Get instant professional improvements to your resume with AI")

# File upload with enhanced UI
with st.expander("📤 Upload Resume", expanded=True):
    uploaded_file = st.file_uploader(
        "Choose a PDF file (max 3 pages, 3MB)",
        type="pdf",
        accept_multiple_files=False,
        key="file_uploader"
    )

# Job targeting
with st.expander("🎯 Target Job (Optional)", expanded=False):
    job_role = st.text_input(
        "Position you're applying for",
        placeholder="e.g., Senior Software Engineer",
        key="job_role"
    )
    company = st.text_input(
        "Company name (optional)",
        placeholder="e.g., Google",
        key="company"
    )

# Processing logic
if uploaded_file:
    # Reset session state if new file uploaded
    if uploaded_file != st.session_state.last_upload:
        st.session_state.last_upload = uploaded_file
        st.session_state.last_response = None
    
    try:
        # Verify file size
        if uploaded_file.size > 3 * 1024 * 1024:
            st.error("❌ File too large. Please upload a smaller file (max 3MB).")
            st.stop()

        # Extract text from PDF with better error handling
        try:
            pdf = PdfReader(BytesIO(uploaded_file.read()))
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            
            if not text.strip():
                st.error("❌ Couldn't extract text from PDF. Please upload a text-based PDF.")
                st.stop()
                
            if len(pdf.pages) > 3:
                st.warning("⚠️ For best results, please upload a 1-3 page resume.")

        except Exception as e:
            st.error(f"❌ PDF processing error: {str(e)}")
            st.stop()

        # Process resume when button clicked
        if st.button("✨ Enhance My Resume", type="primary", key="enhance_button"):
            with st.spinner("🔍 AI is analyzing your resume..."):
                start_time = time.time()
                
                # ===== UPDATED HEADERS FORMAT =====
                headers = {
                    "Authorization": f"Bearer {st.secrets['OPENROUTER_KEY']}",  # No space after "Bearer"
                    "HTTP-Referer": st.secrets.get("APP_URL", "https://default.streamlit.app"),
                    "X-Title": "Resume Rewriter (Production)",
                    "Content-Type": "application/json"
                }
                
                prompt = f"""Improve this resume for a {job_role if job_role else 'general'} position{
                    f' at {company}' if company else ''}. Follow these rules:
                    1. Maintain all original information
                    2. Enhance wording and professionalism
                    3. Optimize for ATS systems
                    4. Keep the same format (bullet points, sections, etc.)
                    5. Return ONLY the improved text, no commentary
                    
                    Original resume:\n{text}"""
                
                try:
                    # ===== REINFORCED API CALL =====
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": "mistralai/mistral-7b-instruct",
                            "messages": [{
                                "role": "user",
                                "content": prompt
                            }],
                            "temperature": 0.3,
                            "max_tokens": 2000
                        },
                        timeout=45,
                        verify=True  # Enforce SSL verification
                    )
                    
                    # Store response in session state
                    st.session_state.last_response = response
                    processing_time = time.time() - start_time
                    
                    # ===== ADDED DEBUG OUTPUT =====
                    st.code(f"""
                    Status: {response.status_code}
                    Headers Sent: {json.dumps(headers, indent=2)}
                    Response: {response.text}
                    """)
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"🌐 Network error: {str(e)}")
                    st.stop()

                # Response validation
                if response.status_code != 200:
                    error_msg = response.json().get("error", {}).get("message", "Unknown API error")
                    st.error(f"🚨 API Error: {error_msg}")
                    st.stop()

                try:
                    data = response.json()
                    if "choices" not in data or len(data["choices"]) == 0:
                        st.error("❌ Unexpected API response format")
                        st.stop()

                    improved_resume = data["choices"][0]["message"]["content"]
                    
                    # Display results
                    st.success(f"✅ Resume enhanced in {processing_time:.1f} seconds!")
                    st.markdown("---")
                    
                    with st.expander("🔍 View Improved Resume", expanded=True):
                        st.markdown(improved_resume)
                    
                    # Download button
                    st.download_button(
                        "⬇️ Download Improved Resume",
                        improved_resume,
                        file_name=f"improved_resume_{job_role or 'general'}.txt",
                        mime="text/plain",
                        key="download_button"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
                    st.stop()

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.stop()

# Debug section (comment out in production)
if st.session_state.last_response:
    with st.expander("Debug Info", expanded=False):
        st.json(st.session_state.last_response.json())
