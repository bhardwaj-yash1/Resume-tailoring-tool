import requests
import json
import os
import dotenv

api_key=os.getenv("api_key")

OPENROUTER_API_URL= "https://openrouter.ai/api/v1/chat/completions"

def resume_tailoring_tool(resume_text: str, jd_text: str, latex_code: str, api_key: str)-> dict:

    prompt= f"""
     
    you are professional resume tailoring assisstant. You stick to the format and maintain the same margins and vibe of the resume 
    , just make changes by using keywords and by analyzing the job description carefully and align the final resume with the given job description.

    my resume text:
    {resume_text}
    
    job description:
    {jd_text}

    latex code:
    {latex_code}

    Task:
    - Rewrite the resume so it highlights the required skills & responsibilities.
    - Keep truthfulness (do not invent experiences).
    - Use concise, ATS-friendly language.
    - extract the resume fields and add the tailored content to the fields in the tailored form
    - Return the resume strictly in valid JSON with these extracted fields.
     
       """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Resume Tailoring Tool"
    }

    payload = {
        "model": "x-ai/grok-4-fast:free",   # you can swap with claude, llama3, etc.
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for tailoring resumes."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response= requests.post(OPENROUTER_API_URL,headers=headers,json=payload)
    

    # tailored_json_str = result["choices"][0]["message"]["content"]

    try:
        # tailored_content=json.loads(tailored_json_str)
        result=response.text()
        return result
    
    except json.JSONDecodeError:
        print("⚠️ LLM did not return valid JSON. Raw output:", result)
        result={}
        return result
        