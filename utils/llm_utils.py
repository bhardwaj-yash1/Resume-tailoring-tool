import requests
import json
import os
import dotenv



OPENROUTER_API_URL= "https://openrouter.ai/api/v1/chat/completions"
        
def resume_tailoring_tool(resume_text: str, jd_text: str, latex_code: str, api_key: str) -> dict:

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
{jd_text}

Original LaTeX template:
{latex_code}

Original resume text (plain):
{resume_text}
"""

    
    headers = {
        "Authorization": f"Bearer {api_key}",  # use the argument, not global
        # "HTTP-Referer": "http://localhost",
        # "X-Title": "Resume Tailoring Tool"
    }

    payload = {
        "model": "x-ai/grok-4-fast:free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for tailoring resumes."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    try:
         result = response.json()

         if "choices" in result and len(result["choices"]) > 0:
             tailored_content = result["choices"][0]["message"]["content"]
         elif "error" in result:
             print("⚠️ API returned an error:", result["error"])
             tailored_content = ""
         else:
             print("⚠️ Unexpected response format:", result)
             tailored_content = ""

         return tailored_content

    except json.JSONDecodeError:
         print("⚠️ Could not decode JSON. Raw response:", response.text)
         return ""
