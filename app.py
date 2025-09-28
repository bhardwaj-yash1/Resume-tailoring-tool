import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Resume Tailoring Tool",
    page_icon="📄",
    layout="centered"
)

# --- Backend API URL ---
API_URL = "http://127.0.0.1:8000/tailor-resume/"

# --- UI Components ---
st.title("📄✨ Resume Tailoring Tool")
st.markdown(
    "Upload your resume, paste the job description, and provide a LaTeX template to get a tailored resume ready to go!"
)

# --- Session State Initialization ---
# This helps preserve state across reruns (e.g., after a failed attempt)
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'pdf_result' not in st.session_state:
    st.session_state.pdf_result = None
if 'show_download' not in st.session_state:
    st.session_state.show_download = False

# --- Input Form ---
with st.form("resume_form", clear_on_submit=False):
    st.header("1. Enter Your Credentials")
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        placeholder="Enter your API key here",
        help="Your API key is required to process the documents."
    )

    st.header("2. Upload Your Documents")
    resume_pdf_file = st.file_uploader(
        "Upload Your Resume (PDF)",
        type="pdf"
    )
    latex_template_file = st.file_uploader(
        "Upload Your LaTeX Template (.tex)",
        type="tex"
    )

    st.header("3. Paste the Job Description")
    job_description = st.text_area(
        "Job Description",
        height=250,
        placeholder="Paste the full job description here..."
    )

    st.markdown("---")
    submitted = st.form_submit_button(
        "🚀 Tailor My Resume",
        use_container_width=True
    )

# --- Form Submission Logic ---
if submitted:
    # Reset state on new submission
    st.session_state.error_message = None
    st.session_state.pdf_result = None
    st.session_state.show_download = False
    
    # Input validation
    if not all([api_key, resume_pdf_file, latex_template_file, job_description]):
        st.warning("Please fill in all the fields before submitting.")
    else:
        with st.spinner("Processing... This may take a moment. 🤖"):
            try:
                # Prepare files and data for the API request
                files = {
                    'resume_pdf': (resume_pdf_file.name, resume_pdf_file, 'application/pdf'),
                    'latex_template': (latex_template_file.name, latex_template_file, 'application/x-tex')
                }
                data = {
                    'api_key': api_key,
                    'job_description': job_description
                }

                # Make the POST request to the backend
                response = requests.post(API_URL, files=files, data=data, timeout=300)

                # Handle the response
                if response.status_code == 200:
                    st.session_state.pdf_result = response.content
                    st.session_state.show_download = True
                else:
                    # Capture error detail from FastAPI
                    error_data = response.json()
                    st.session_state.error_message = error_data.get('detail', 'An unknown error occurred.')

            except requests.exceptions.RequestException as e:
                st.session_state.error_message = f"Failed to connect to the backend API. Please ensure it's running. Error: {e}"

# --- Display Results or Errors ---
if st.session_state.error_message:
    st.error(f"**An error occurred:**\n\n{st.session_state.error_message}")
    st.info("Please correct the issue (e.g., check your LaTeX template) and try again.")

if st.session_state.show_download and st.session_state.pdf_result:
    st.success("✅ Your tailored resume is ready!")
    st.download_button(
        label="📥 Download Tailored Resume (PDF)",
        data=st.session_state.pdf_result,
        file_name="tailored_resume.pdf",
        mime="application/pdf",
        use_container_width=True
    )
