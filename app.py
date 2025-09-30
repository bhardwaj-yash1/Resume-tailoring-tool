# import streamlit as st
# import requests

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="Resume Tailoring Tool",
#     page_icon="📄",
#     layout="centered"
# )

# # VITAL: REPLACE WITH YOUR ACTUAL RENDER API URL
# # This should be the public URL provided by Render for your backend service.
# API_URL = "https://resume-tailoring-tool-1.onrender.com/tailor-resume/"


# # --- UI Components ---
# st.title("📄✨ Resume Tailoring Tool")
# st.markdown(
#     "Upload your resume, paste the job description, and provide a LaTeX template to get a tailored resume ready to go!"
# )

# # --- Session State Initialization ---
# if 'error_message' not in st.session_state:
#     st.session_state.error_message = None
# if 'pdf_result' not in st.session_state:
#     st.session_state.pdf_result = None
# if 'show_download' not in st.session_state:
#     st.session_state.show_download = False

# # --- Input Form ---
# with st.form("resume_form", clear_on_submit=False):
#     st.header("1. Enter Your Credentials")
#     api_key = st.text_input(
#         "OpenRouter API Key",
#         type="password",
#         placeholder="Enter your API key here",
#         help="Your API key is required to process the documents."
#     )

#     st.header("2. Upload Your Documents")
#     resume_pdf_file = st.file_uploader(
#         "Upload Your Resume (PDF)",
#         type="pdf"
#     )
#     latex_template_file = st.file_uploader(
#         "Upload Your LaTeX Template (.tex)",
#         type="tex"
#     )

#     st.header("3. Paste the Job Description")
#     job_description = st.text_area(
#         "Job Description",
#         height=250,
#         placeholder="Paste the full job description here..."
#     )

#     st.markdown("---")
#     submitted = st.form_submit_button(
#         "🚀 Tailor My Resume",
#         use_container_width=True
#     )

# # --- Form Submission Logic ---
# if submitted:
#     # Reset state on new submission
#     st.session_state.error_message = None
#     st.session_state.pdf_result = None
#     st.session_state.show_download = False
    
#     # Input validation
#     if not all([api_key, resume_pdf_file, latex_template_file, job_description]):
#         st.warning("Please fill in all the fields before submitting.")
#     else:
#         with st.spinner("Processing... This may take a moment. 🤖"):
#             try:
#                 # Prepare files and data for the multipart/form-data request
#                 files = {
#                     'resume_pdf': (resume_pdf_file.name, resume_pdf_file.getvalue(), 'application/pdf'),
#                     'latex_template': (latex_template_file.name, latex_template_file.getvalue(), 'application/x-tex')
#                 }
#                 data = {
#                     'api_key': api_key,
#                     'job_description': job_description
#                 }

#                 # Make the POST request to the backend with files and data
#                 response = requests.post(
#                     API_URL,
#                     files=files,
#                     data=data
#                 )

#                 # Handle the response
#                 if response.status_code == 200:
#                     st.session_state.pdf_result = response.content
#                     st.session_state.show_download = True
#                 else:
#                     # Capture error detail from FastAPI
#                     error_data = response.json()
#                     detail = error_data.get('detail', 'An unknown error occurred.')
#                     st.session_state.error_message = f"Error from API (Status {response.status_code}): {detail}"

#             except requests.exceptions.RequestException as e:
#                 st.session_state.error_message = f"Failed to connect to the backend API. Please ensure it's running. Error: {e}"

# # --- Display Results or Errors ---
# if st.session_state.error_message:
#     st.error(f"**An error occurred:**\n\n{st.session_state.error_message}")
#     st.info("Please correct the issue and try again. If the error is about LaTeX compilation, check your .tex template for syntax errors.")

# if st.session_state.show_download and st.session_state.pdf_result:
#     st.success("✅ Your tailored resume is ready!")
#     st.download_button(
#         label="📥 Download Tailored Resume (PDF)",
#         data=st.session_state.pdf_result,
#         file_name="tailored_resume.pdf",
#         mime="application/pdf",
#         use_container_width=True
#     )

import streamlit as st
import requests
import fitz  # PyMuPDF
import subprocess
import os
import tempfile
import json # Import the json library

# --- ⚙️ Helper Functions (Backend Logic) ---

def extract_text_from_pdf(pdf_file):
    """Reads an uploaded PDF file and returns its text content."""
    # ... (This function remains the same) ...
    try:
        pdf_document = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {e}")

def call_openrouter_llm(api_key, resume_text, job_description, template_text):
    """Calls the OpenRouter API and returns the tailored LaTeX content."""
    prompt = f"""
    You are an expert resume writer. Your task is to tailor the provided resume content to the job description using the given LaTeX template.
    
    1. **Resume Content**:
    {resume_text}

    2. **Job Description**:
    {job_description}

    3. **LaTeX Template**:
    ```latex
    {template_text}
    ```

    **Instructions**:
    - Fill in the LaTeX template with the resume content.
    - Modify the content to highlight skills and experiences relevant to the job description.
    - Ensure the output is ONLY the complete, valid LaTeX code for the tailored resume.
    - **CRITICAL**: You MUST escape all special LaTeX characters in the content you generate. For example, replace '&' with '\\&', '%' with '\\%', '$' with '\\$', '#' with '\\#', and '_' with '\\_'. This is the most important rule.
    """
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo", # Or your preferred good model
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=180
        )
        response.raise_for_status() # Check for HTTP errors like 401, 429, etc.
        
        # Try to parse the JSON and get the content
        data = response.json()
        tailored_latex = data['choices'][0]['message']['content']
        
        # Clean up the response
        if tailored_latex.strip().startswith("```latex"):
            tailored_latex = tailored_latex.strip()[7:]
            if tailored_latex.strip().endswith("```"):
                tailored_latex = tailored_latex.strip()[:-3]
        return tailored_latex

    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors specifically
        raise ValueError(f"HTTP Error from API: {http_err}\nResponse Body: {response.text}")
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # This catches cases where the response is not valid JSON or has an unexpected structure
        # This is the MOST LIKELY place the error is happening.
        raise ValueError(f"API returned an unexpected response. It might be a rate limit or API key issue. Raw Response: \n\n{response.text}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API Request Failed: {e}")


def compile_latex_to_pdf(latex_string):
    """Compiles a string of LaTeX code into a PDF and returns the PDF bytes."""
    # ... (This function remains the same) ...
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(temp_dir, "tailored.tex")
        pdf_path = os.path.join(temp_dir, "tailored.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_string)

        try:
            # Run pdflatex twice
            for _ in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
            else:
                raise RuntimeError("PDF file was not generated despite successful compilation.")
        except subprocess.CalledProcessError as e:
            # Raise an exception with the detailed log
            raise RuntimeError(f"LaTeX Compilation Failed. Log:\n{e.stdout}\n{e.stderr}")

# --- 🖼️ Streamlit UI ---

st.set_page_config(page_title="Resume Tailoring Tool", page_icon="📄", layout="centered")

st.title("📄✨ Resume Tailoring Tool")
# ... (UI text remains the same) ...

if 'pdf_result' not in st.session_state:
    st.session_state.pdf_result = None

with st.form("resume_form"):
    # ... (Form elements remain the same) ...
    st.header("1. Your Credentials")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.header("2. Your Documents")
    resume_pdf_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")
    latex_template_file = st.file_uploader("Upload Your LaTeX Template (.tex)", type="tex")
    st.header("3. The Job")
    job_description = st.text_area("Job Description", height=250)
    submitted = st.form_submit_button("🚀 Tailor My Resume", use_container_width=True)


if submitted:
    st.session_state.pdf_result = None
    if not all([api_key, resume_pdf_file, latex_template_file, job_description]):
        st.warning("Please fill in all the fields.")
    else:
        with st.spinner("Processing... This may take a few minutes. 🤖"):
            try:
                # --- THIS IS THE UPDATED LOGIC ---
                template_text = latex_template_file.read().decode("utf-8")
                resume_text = extract_text_from_pdf(resume_pdf_file)
                
                tailored_latex = call_openrouter_llm(api_key, resume_text, job_description, template_text)
                
                pdf_bytes = compile_latex_to_pdf(tailored_latex)
                
                st.session_state.pdf_result = pdf_bytes
            
            except (ValueError, RuntimeError) as e:
                # Catch the specific errors from our helper functions and display them
                st.error(str(e))


if st.session_state.pdf_result:
    st.success("✅ Your tailored resume is ready!")
    st.download_button(
        label="📥 Download Tailored Resume (PDF)",
        data=st.session_state.pdf_result,
        file_name="tailored_resume.pdf",
        mime="application/pdf",
        use_container_width=True
    )