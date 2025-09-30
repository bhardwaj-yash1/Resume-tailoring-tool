# streamlit_app.py
import streamlit as st
import requests
from io import BytesIO
import os

st.set_page_config(page_title="Resume Tailoring Tool", layout="centered")

st.title("Resume Tailoring Tool")
st.write("Upload your resume (PDF), LaTeX template (.tex) and paste the job description. The backend will call the LLM and compile the tailored PDF.")

API_URL = st.text_input("Backend URL (FastAPI)", value=os.getenv("BACKEND_URL", "https://resume-tailoring-tool.onrender.com/"))

with st.form("tailor_form"):
    resume_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
    latex_file = st.file_uploader("Upload LaTeX template (.tex)", type=["tex"])
    jd_text = st.text_area("Job Description (paste here)", height=200)
    api_key_input = st.text_input("OpenRouter API Key (optional; leave blank to use backend env var)", type="password")
    keep_files = st.checkbox("Keep temp files on backend (for debugging)", value=False)
    submit = st.form_submit_button("Tailor Resume")

if submit:
    if not resume_file or not latex_file or not jd_text.strip():
        st.error("Please provide resume PDF, LaTeX template and job description.")
    else:
        with st.spinner("Sending data to backend... this may take 30–90s depending on LLM/compilation"):
            try:
                files = {
                    "resume_pdf": ("resume.pdf", resume_file.getvalue(), "application/pdf"),
                    "latex_template": ("template.tex", latex_file.getvalue(), "text/x-tex"),
                }
                data = {
                    "jd_text": jd_text,
                    "keep_files": str(keep_files).lower()
                }
                if api_key_input:
                    data["api_key"] = api_key_input

                # make multipart POST
                resp = requests.post(API_URL, files=files, data=data, timeout=300)  # generous timeout

                if resp.status_code == 200 and resp.headers.get("content-type","").startswith("application/pdf"):
                    st.success("Tailored PDF ready!")
                    # offer download
                    st.download_button(
                        label="Download tailored PDF",
                        data=resp.content,
                        file_name="tailored_resume.pdf",
                        mime="application/pdf"
                    )
                else:
                    # try to parse JSON response
                    try:
                        j = resp.json()
                        st.error(f"Backend error: {j.get('error', 'Unknown error')}")
                        tailor_tex = j.get("tailored_latex", "")
                        if tailor_tex:
                            st.subheader("Tailored LaTeX (download / edit and retry)")
                            st.code(tailor_tex, language="latex")
                            st.download_button("Download tailored LaTeX", data=tailor_tex, file_name="tailored.tex", mime="text/x-tex")
                    except Exception:
                        st.error(f"Unexpected response: {resp.status_code}")
                        st.text(resp.text[:2000])

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {str(e)}")
