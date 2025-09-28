import requests
import json
import os
import dotenv



OPENROUTER_API_URL= "https://openrouter.ai/api/v1/chat/completions"
        
def resume_tailoring_tool(resume_text: str, jd_text: str, latex_code: str, api_key: str) -> dict:

    prompt = f"""
You are a professional resume assistant.

Task:
- Take the following LaTeX resume template and the plain text resume.
- Tailor the content according to the job description.
- Do NOT change LaTeX formatting, packages, or commands.
- Only modify the content inside each field (education, projects, experience, skills, summary, etc.)
- Keep everything ATS-friendly and truthful.
- DO NOT change the core of the resume and do NOT add fake stuff.
- maintain the originality of the projects and their truthfullness
- analyze everything deeply and then perform tailoring of the resume.
- Return the full LaTeX code, ready to compile, as your output. Do NOT return JSON.

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
