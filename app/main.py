from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tempfile import TemporaryDirectory
import shutil
import os

from tailor_resume import resume_tailoring_pipeline

app = FastAPI(title="Resume Tailoring API")

# Allow CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tailor_resume")
async def tailor_resume(
    resume_pdf: UploadFile,
    latex_template: UploadFile,
    jd_text: str = Form(...),
    api_key: str = Form(None),
    keep_files: str = Form("false")
):
    keep_files_bool = keep_files.lower() == "true"

    try:
        with TemporaryDirectory() as temp_dir:
            # Save uploaded files
            resume_path = os.path.join(temp_dir, "resume.pdf")
            latex_path = os.path.join(temp_dir, "template.tex")
            output_tex_path = os.path.join(temp_dir, "tailored.tex")
            output_pdf_path = os.path.join(temp_dir, "tailored.pdf")

            with open(resume_path, "wb") as f:
                f.write(await resume_pdf.read())

            with open(latex_path, "wb") as f:
                f.write(await latex_template.read())

            # Save JD text
            jd_path = os.path.join(temp_dir, "jd.txt")
            with open(jd_path, "w", encoding="utf-8") as f:
                f.write(jd_text)

            # Run the pipeline
            final_pdf = resume_tailoring_pipeline(
                pdf_path=resume_path,
                latex_path=latex_path,
                jd_path=jd_path,
                api_key=api_key,
                saving_path=output_tex_path,
                output_latex_path=output_tex_path
            )

            if final_pdf and os.path.exists(final_pdf):
                return FileResponse(final_pdf, media_type="application/pdf", filename="tailored_resume.pdf")
            else:
                return JSONResponse({"error": "Tailoring failed"}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
