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


import re

import re

def extract_sections(latex_text):
    # Split by \section{}, keep the header
    pattern = r"(\\section\{.*?\})"
    headers = re.findall(pattern, latex_text)
    
    sections = {}
    for i, header in enumerate(headers):
        start = latex_text.find(header)
        end = latex_text.find(headers[i+1]) if i+1 < len(headers) else len(latex_text)
        sections[header] = latex_text[start+len(header):end].strip()
    return sections



def tailor_section(section_name, section_content, resume_text, jd_text, latex_template, api_key):
    prompt = f"""
You are a professional resume assistant.

Task:
- Take the following LaTeX resume section and tailor it using the resume content.
- Do NOT modify LaTeX commands or formatting.
- Only fill the content inside the section.
- Keep it ATS-friendly, concise, keyword-rich, and truthful.
- Use information from the original resume text to rewrite or expand the section.
- Job description must guide your adjustments.

Section name: {section_name}
Original section content (LaTeX):
{section_content}

Full LaTeX template (for reference):
{latex_template}

Original resume text:
{resume_text}

Job description:
{jd_text}

Return only the LaTeX code of this section (header + content). Do NOT return JSON.
"""
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for tailoring resumes."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    import requests
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    try:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            print("⚠️ API returned an error:", result["error"])
            return section_content
        else:
            print("⚠️ Unexpected response format:", result)
            return section_content
    except:
        print("⚠️ Could not decode JSON. Raw response:", response.text)
        return section_content

sections = extract_sections(latex_code)
final_latex = latex_code

for header, content in sections.items():
    new_section = tailor_section(header, content, resume_text, jd, latex_code, api)
    final_latex = final_latex.replace(header + content, new_section)

save_latex_code(latex=final_latex,save_path=saving_path)