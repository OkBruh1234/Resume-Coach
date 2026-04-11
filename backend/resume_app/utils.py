import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def analyze_resume_with_rag(resume_text: str, job_description: str) -> dict:
    """
    Passes the complete resume and JD directly to Gemini 1.5 Flash leveraging
    its massive 1M token context window!
    """
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")

    print("1. Sending complete Resume and JD straight to Google AI Studio Gemini Flash...")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", max_tokens=800)
    
    prompt = PromptTemplate.from_template(
        """You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
        Below is the candidate's complete resume text, and their target Job Description.
        
        Job Description:
        {job_description}
        
        Resume Text:
        {context}
        
        Evaluate the resume against the Job Description. Provide a JSON response EXACTLY in the following format with no code blocks or extra text:
        {{
            "ats_match_level": "High",
            "ats_score": "85", 
            "gap_analysis": {{
                "missing_keywords": ["keyword1", "keyword2"],
                "suggestions": "A specific sentence on how they can improve based strictly on the missing gaps."
            }}
        }}
        
        CRITICAL RULES:
        1. `ats_match_level` MUST be exactly one of: "Low", "Medium", or "High".
        2. `ats_score` MUST be a pure number out of 100 representing the exact percentage match (e.g. "85", "92", "45").
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    result_str = chain.invoke({"context": resume_text, "job_description": job_description})
    
    result_str = result_str.strip()
    if result_str.startswith("```json"):
        result_str = result_str[7:-3].strip()
    elif result_str.startswith("```"):
        result_str = result_str[3:-3].strip()
        
    try:
        result_json = json.loads(result_str)
        return result_json
    except Exception as e:
        return {
            "ats_score": "Unknown",
            "gap_analysis": {
                "missing_keywords": [],
                "suggestions": f"Failed to parse LLM response: {result_str}. Error: {e}"
            }
        }
