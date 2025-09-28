# import os
# from dotenv import load_dotenv
# load_dotenv()
# from utils.llm_utils import resume_tailoring_tool
# from utils.pdf_and_latex_utils import read_pdf, save_latex_code, latex_to_pdf
# from typing import Optional

# pdf_path=os.getenv("pdf_path")
# latex_path=os.getenv("latex_path")
# jd_path=os.getenv("jd_path")
# api=os.getenv("api_key")
# saving_path=os.getenv("saving_path")
# output_latex_path=os.getenv("output_latex_path")

# import os
# print("Path exists?", os.path.exists(pdf_path))

# resume_text=read_pdf(pdf_path=pdf_path)

# with open(latex_path,"r",encoding="utf-8") as f:
#     latex_code= f.read()

# with open(jd_path,"r",encoding="utf-8") as f:
#     jd= f.read()

# updated_latex=resume_tailoring_tool(resume_text=resume_text,jd_text=jd,latex_code=latex_code,api_key=api)

# save_latex_code(latex=updated_latex,save_path=saving_path)

# final_pdf_path=latex_to_pdf(output_latex_path)

import os
from dotenv import load_dotenv
from utils.llm_utils import resume_tailoring_tool
from utils.pdf_and_latex_utils import read_pdf, save_latex_code, latex_to_pdf
from typing import Optional

load_dotenv()

def resume_tailoring_pipeline(
    pdf_path: Optional[str] = None,
    latex_path: Optional[str] = None,
    jd_path: Optional[str] = None,
    api_key: Optional[str] = None,
    saving_path: Optional[str] = None,
    output_latex_path: Optional[str] = None
) -> str:
    """
    Complete pipeline for tailoring a resume:
    1. Reads plain text from a PDF resume.
    2. Reads LaTeX resume template and job description.
    3. Uses LLM to tailor resume content (truthful, ATS-friendly).
    4. Saves tailored LaTeX code.
    5. Compiles LaTeX to PDF.

    Returns:
        final_pdf_path (str): Path to the compiled tailored resume PDF.
    """

    # Load environment variables if not passed directly
    pdf_path = pdf_path or os.getenv("pdf_path")
    latex_path = latex_path or os.getenv("latex_path")
    jd_path = jd_path or os.getenv("jd_path")
    api_key = api_key or os.getenv("api_key")
    saving_path = saving_path or os.getenv("saving_path")
    output_latex_path = output_latex_path or os.getenv("output_latex_path")

    # Debugging info
    print("Checking paths...")
    for path_label, path in {
        "PDF": pdf_path,
        "LaTeX Template": latex_path,
        "Job Description": jd_path,
    }.items():
        print(f"{path_label} exists? {os.path.exists(path)}")

    # Step 1: Read plain text from resume PDF
    resume_text = read_pdf(pdf_path=pdf_path)

    # Step 2: Load LaTeX template and Job Description
    with open(latex_path, "r", encoding="utf-8") as f:
        latex_code = f.read()

    with open(jd_path, "r", encoding="utf-8") as f:
        jd = f.read()

    # Step 3: Call the tailoring tool (LLM)
    updated_latex = resume_tailoring_tool(
        resume_text=resume_text,
        jd_text=jd,
        latex_code=latex_code,
        api_key=api_key
    )

    # Step 4: Save tailored LaTeX code
    save_latex_code(latex=updated_latex, save_path=saving_path)

    # Step 5: Compile LaTeX to PDF
    final_pdf_path = latex_to_pdf(output_latex_path)

    print(f"✅ Pipeline completed. Final tailored PDF at: {final_pdf_path}")
    return final_pdf_path


# Example usage (if you want to call directly from main.py)
if __name__ == "__main__":
    resume_tailoring_pipeline()

