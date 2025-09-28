import os
from dotenv import load_dotenv
load_dotenv()
from utils.llm_utils import resume_tailoring_tool
from utils.pdf_utils import read_pdf, save_latex_code

pdf_path=os.getenv("pdf_path")
latex_path=os.getenv("latex_path")
jd_path=os.getenv("jd_path")
api=os.getenv("api_key")
saving_path=os.getenv("saving_path")

import os
print("Path exists?", os.path.exists(pdf_path))

resume_text=read_pdf(pdf_path=pdf_path)

with open(latex_path,"r",encoding="utf-8") as f:
    latex_code= f.read()

with open(jd_path,"r",encoding="utf-8") as f:
    jd= f.read()

updated_latex=resume_tailoring_tool(resume_text=resume_text,jd_text=jd,latex_code=latex_code,api_key=api)

save_latex_code(latex=updated_latex,save_path=saving_path)

