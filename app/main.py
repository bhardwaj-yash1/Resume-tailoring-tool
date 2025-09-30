# app/main.py
import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import your pipeline
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # add repo root to path
from tailor_resume import resume_tailoring_pipeline

app = FastAPI(title="Resume Tailoring API")

# Allow CORS from typical frontends (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your streamlit frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = Path(os.getenv("TMP_DIR", "/tmp/resume_tailor"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

def _save_upload(upload_file: UploadFile, dest: Path) -> None:
    with dest.open("wb") as f:
        shutil.copyfileobj(upload_file.file, f)

@app.post("/api/tailor")
async def tailor(
    resume_pdf: UploadFile = File(...),
    latex_template: UploadFile = File(...),
    jd_text: str = Form(...),
    api_key: str = Form(None),
    keep_files: bool = Form(False)
):
    """
    Accepts:
    - resume_pdf: uploaded PDF (the user's resume)
    - latex_template: uploaded .tex template
    - jd_text: job description text
    - api_key: optional OpenRouter API key (if not provided, will use env var API_KEY)
    - keep_files: optional flag to keep temp files on server for debugging
    Returns:
    - on success: PDF file (FileResponse)
    - on latex compile error: JSON { "error": "...", "tailored_latex": "<string>" }
    """
    job_id = uuid.uuid4().hex[:12]
    workdir = TMP_DIR / f"job_{job_id}"
    workdir.mkdir(parents=True, exist_ok=True)

    try:
        # Save uploaded resume PDF
        resume_path = workdir / "resume_input.pdf"
        _save_upload(resume_pdf, resume_path)

        # Save uploaded latex template
        latex_template_path = workdir / "template.tex"
        _save_upload(latex_template, latex_template_path)

        # Save JD text to file
        jd_path = workdir / "job_description.txt"
        jd_path.write_text(jd_text, encoding="utf-8")

        # Set output .tex and saving paths
        output_latex_path = workdir / "tailored.tex"     # what pdflatex will run on
        saving_path = str(output_latex_path)

        # Determine API key to pass to the pipeline
        env_api_key = api_key or os.getenv("API_KEY")
        if not env_api_key:
            raise HTTPException(status_code=400, detail="No API key provided (form or env var API_KEY).")

        # Call your pipeline (synchronous)
        final_pdf_path = resume_tailoring_pipeline(
            pdf_path=str(resume_path),
            latex_path=str(latex_template_path),
            jd_path=str(jd_path),
            api_key=env_api_key,
            saving_path=str(saving_path),
            output_latex_path=str(output_latex_path)
        )

        # resume_tailoring_pipeline returns the final PDF path on success or None on failure
        if final_pdf_path and os.path.exists(final_pdf_path):
            # return PDF
            return FileResponse(path=final_pdf_path, filename=f"tailored_{job_id}.pdf", media_type="application/pdf")
        else:
            # If compile failed, try to read the tailored .tex (if produced) and return it for retry
            tailored_latex = ""
            if output_latex_path.exists():
                tailored_latex = output_latex_path.read_text(encoding="utf-8")
            return JSONResponse(status_code=500, content={
                "error": "LaTeX compilation failed. Please retry or edit the returned LaTeX.",
                "tailored_latex": tailored_latex
            })

    except HTTPException as he:
        raise he

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Server error: {str(e)}"})

    finally:
        # cleanup unless keep_files True
        if not keep_files:
            try:
                shutil.rmtree(workdir)
            except Exception:
                pass
