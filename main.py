import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from tailor_resume import resume_tailoring_pipeline

app = FastAPI()

# Create a temporary directory for file storage
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/tailor-resume/")
async def tailor_resume_endpoint(
    api_key: str = Form(...),
    resume_pdf: UploadFile = File(...),
    latex_template: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Endpoint to tailor a resume.
    Receives an API key, resume PDF, LaTeX template, and job description.
    Processes them and returns the tailored PDF.
    """
    # Create a unique subdirectory for this request to handle concurrent requests
    request_id = str(uuid.uuid4())
    request_dir = os.path.join(TEMP_DIR, request_id)
    os.makedirs(request_dir, exist_ok=True)

    try:
        # Define file paths within the unique directory
        pdf_path = os.path.join(request_dir, resume_pdf.filename)
        latex_path = os.path.join(request_dir, latex_template.filename)
        jd_path = os.path.join(request_dir, "jd.txt")
        
        # The output files will also be saved in this unique directory
        # This matches the expected format for the pipeline
        output_latex_name = os.path.splitext(latex_template.filename)[0] + "_tailored.tex"
        saving_path = os.path.join(request_dir, output_latex_name)

        # Save the uploaded files and job description
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(resume_pdf.file, f)

        with open(latex_path, "wb") as f:
            shutil.copyfileobj(latex_template.file, f)
            
        with open(jd_path, "w", encoding="utf-8") as f:
            f.write(job_description)

        print(f"✅ Files saved for request {request_id}")

        # Run the resume tailoring pipeline
        final_pdf_path = resume_tailoring_pipeline(
            pdf_path=pdf_path,
            latex_path=latex_path,
            jd_path=jd_path,
            api_key=api_key,
            saving_path=saving_path,
            output_latex_path=saving_path # The input for compilation is the saved tailored .tex file
        )
        
        if final_pdf_path and os.path.exists(final_pdf_path):
            # If successful, return the generated PDF
            return FileResponse(
                path=final_pdf_path,
                media_type='application/pdf',
                filename='tailored_resume.pdf'
            )
        else:
            # If compilation fails, the pipeline returns None
            raise HTTPException(
                status_code=500,
                detail="LaTeX compilation failed. Please check your LaTeX template for errors and try again."
            )

    except Exception as e:
        # Catch any other exceptions
        print(f"❌ An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the request-specific directory after processing
        if os.path.exists(request_dir):
            shutil.rmtree(request_dir)
            print(f"🧹 Cleaned up directory: {request_dir}")

@app.get("/")
def read_root():
    return {"message": "Resume Tailoring API is running."}
