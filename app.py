import streamlit as st
import requests
import fitz  # PyMuPDF
import subprocess
import os
import tempfile
import json

# --- ⚙️ Backend Logic (Combined from your utils files) ---

def extract_text_from_pdf_upload(pdf_file_upload):
    """Reads an uploaded PDF file from Streamlit and returns its text."""
    try:
        # Use getvalue() to read the bytes from the uploaded file
        pdf_document = fitz.open(stream=pdf_file_upload.getvalue(), filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        return text
    except Exception as e:
        # Raise a specific error that can be caught and displayed in the UI
        raise ValueError(f"Error reading PDF file. It might be corrupted or in an unexpected format. Details: {e}")

def call_llm_for_tailoring(api_key, resume_text, job_description, template_text):
    """Calls the OpenRouter API to get the tailored LaTeX content."""
    prompt = f"""
    You are a highly skilled professional resume assistant and LaTeX expert.

    Task:
    1. You are given:
        - A plain text resume
        - A LaTeX resume template
        - A job description
    2. Your job is to **tailor the resume to the job description** while keeping it:
        - **Truthful**: Do NOT add any fake or fabricated information.
        - **Original**: Do not change the core meaning of project descriptions, experience, or other sections.
        - **Relevant**: Only add keywords or phrasing from the job description where appropriate.
        - **ATS-friendly**: Keep it suitable for applicant tracking systems.
    3. **LaTeX instructions**:
        - Do NOT modify any LaTeX packages, formatting, or commands.
        - Only change the **content inside the fields** (education, projects, experience, skills, summary, etc.)
        - Ensure the output **compiles without errors**.
        - Maintain correct LaTeX syntax strictly.
        - Single page only
        - maintain same description length for every section
    4. **Context awareness**:
        - Keep descriptions consistent with the heading context. For example, project content stays as a project; do not turn it into learning content or exaggerate.
        - If a skill or project detail is not relevant to the job description, you can **slightly rephrase** to highlight relevant parts, but never invent new experiences or outcomes.

    **Output instructions**:
    - Return the **full LaTeX code**, ready to compile.
    - Do NOT return JSON or extra commentary.
    - Ensure **no syntax errors or missing braces/commands**.

    Job description:
    {job_description}

    Original LaTeX template:
    {template_text}

    Original resume text (plain):
    {resume_text}
    """
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "google/gemini-flash-1.5", # Switched to a currently available and capable model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=180 # 3 minutes timeout for the API call
        )
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        tailored_latex = data['choices'][0]['message']['content']

        # Clean up common LLM response artifacts
        if tailored_latex.strip().startswith("```latex"):
            tailored_latex = tailored_latex.strip()[7:]
        if tailored_latex.strip().endswith("```"):
            tailored_latex = tailored_latex.strip()[:-3]

        return tailored_latex

    except requests.exceptions.HTTPError as http_err:
        raise ValueError(f"HTTP Error from API: {http_err}\nResponse Body: {response.text}")
    except (json.JSONDecodeError, KeyError, IndexError):
        raise ValueError(f"API returned an unexpected response. It might be a rate limit or API key issue. Raw Response: \n\n{response.text}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API Request Failed due to a network issue: {e}")

def compile_latex_to_pdf(latex_string):
    """Compiles a string of LaTeX code into a PDF within a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(temp_dir, "tailored.tex")
        pdf_path = os.path.join(temp_dir, "tailored.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_string)

        try:
            # Run pdflatex twice for better results (e.g., for table of contents, references)
            for i in range(2):
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
                # This case is unlikely if subprocess.run succeeds but is good for robustness
                raise RuntimeError("PDF file was not generated despite a seemingly successful compilation.")
        except subprocess.CalledProcessError as e:
            # Raise a specific error with the full LaTeX log
            raise RuntimeError(f"LaTeX Compilation Failed. This usually means the AI generated invalid LaTeX code. Please see the log below:\n\n{e.stdout}\n{e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Critical Error: 'pdflatex' command not found on the server. This indicates a problem with the deployment environment.")

# --- 🖼️ Streamlit UI ---

st.set_page_config(page_title="Resume Tailoring Tool", page_icon="📄", layout="centered")

st.title("📄✨ Resume Tailoring Tool")
st.markdown("Upload your resume, paste a job description, and provide a LaTeX template. Get a tailored PDF resume in seconds!")

# --- Session State Initialization ---
# This ensures that uploaded files are not lost if a compilation fails, allowing for a retry.
if 'pdf_result' not in st.session_state:
    st.session_state.pdf_result = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# --- Input Form ---
with st.form("resume_form"):
    st.header("1. Your Credentials")
    api_key = st.text_input("OpenRouter API Key", type="password", help="Your key is used to process the request and is not stored.")

    st.header("2. Your Documents")
    resume_pdf_file = st.file_uploader("Upload Your Current Resume", type="pdf")
    latex_template_file = st.file_uploader("Upload Your LaTeX Template", type="tex")

    st.header("3. The Job")
    job_description = st.text_area("Paste the Job Description Here", height=250)
    
    submitted = st.form_submit_button("🚀 Tailor My Resume", use_container_width=True)

# --- Processing Logic ---
if submitted:
    # Reset state on a new submission
    st.session_state.pdf_result = None
    st.session_state.error_message = None

    if not all([api_key, resume_pdf_file, latex_template_file, job_description]):
        st.warning("Please fill in all the fields before submitting.")
    else:
        with st.spinner("Processing... This may take a moment. 🤖"):
            try:
                # The main pipeline, now inside the Streamlit app
                template_text = latex_template_file.read().decode("utf-8")
                resume_text = extract_text_from_pdf_upload(resume_pdf_file)
                
                tailored_latex = call_llm_for_tailoring(api_key, resume_text, job_description, template_text)
                
                pdf_bytes = compile_latex_to_pdf(tailored_latex)
                
                # Success!
                st.session_state.pdf_result = pdf_bytes
            
            except (ValueError, RuntimeError) as e:
                # Catch specific errors from our functions and display them clearly
                st.session_state.error_message = str(e)

# --- Display Results or Errors ---
if st.session_state.error_message:
    st.error("An error occurred during processing:")
    st.code(st.session_state.error_message, language='log')
    st.info("The most common issue is the AI generating slightly invalid LaTeX. You can try submitting again. Your uploaded files are still intact.")

if st.session_state.pdf_result:
    st.success("✅ Your tailored resume is ready!")
    st.download_button(
        label="📥 Download Tailored Resume (PDF)",
        data=st.session_state.pdf_result,
        file_name="tailored_resume.pdf",
        mime="application/pdf",
        use_container_width=True
    )

