import os
from utils.llm_utils import resume_tailoring_tool
from utils.pdf_utils import read_pdf

pdf_path=os.getenv("pdf_path")
latex_path=os.getenv("latex_path")
api=os.getenv("api_key")

resume_text=read_pdf(pdf_path=pdf_path)

with open(latex_path,"r",encoding="utf-8") as f:
    latex_code= f.read()

jd=str(input("enter job desc:"))

resume_tailoring_tool(resume_text=resume_text,jd_text=jd,latex_code=latex_code,api_key=api)
