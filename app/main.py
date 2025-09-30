from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import os, uuid, tempfile
from tailor_resume import run_tailoring

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Resume Tailor API is running 🚀"}

@app.post("/")
async def tailor_resume_endpoint(
    resume_pdf: UploadFile = File(...),
    latex_template: UploadFile = File(...),
    jd_text: str = Form(...),
    api_key: str = Form(None),
    keep_files: str = Form("false")
):
    try:
        temp_dir = tempfile.mkdtemp()
        resume_path = os.path.join(temp_dir, "resume.pdf")
        latex_path = os.path.join(temp_dir, "template.tex")

        with open(resume_path, "wb") as f:
            f.write(await resume_pdf.read())
        with open(latex_path, "wb") as f:
            f.write(await latex_template.read())

        pdf_path, latex_code = run_tailoring(
            resume_pdf_path=resume_path,
            latex_template_path=latex_path,
            jd_text=jd_text,
            api_key=api_key,
            keep_files=(keep_files == "true"),
        )

        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                path=pdf_path,
                filename="tailored_resume.pdf",
                media_type="application/pdf"
            )
        else:
            return JSONResponse(
                content={"error": "Tailoring failed", "tailored_latex": latex_code or ""},
                status_code=500
            )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
