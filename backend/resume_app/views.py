import os
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pdfplumber
from .models import ResumeAnalysis

def has_api_key():
    # Check if GEMINI_API_KEY is available in the environment
    return bool(os.environ.get("GEMINI_API_KEY"))

class AnalyzeResumeView(APIView):
    def post(self, request, *args, **kwargs):
        resume_file = request.FILES.get('file')
        job_description = request.data.get('job_description')

        if not resume_file or not job_description:
            return Response({"error": "Missing file or job description"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract text from PDF
        text = ""
        try:
            with pdfplumber.open(resume_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            return Response({"error": f"Failed to parse PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if not has_api_key():
                raise Exception("Missing API Key")
                
            from .utils import analyze_resume_with_rag
            rag_result = analyze_resume_with_rag(text, job_description)
            score = rag_result.get("ats_score", "Unknown")
            match_level = rag_result.get("ats_match_level", "Unknown")
            gaps = rag_result.get("gap_analysis", {})
        except Exception as e:
            error_str = str(e).lower()
            if "key" in error_str or "auth" in error_str or "credentials" in error_str:
                # Graceful Offline Mock Fallback if API Key is missing
                score = "50"
                match_level = "Medium"
                gaps = {
                    "missing_keywords": ["Valid GEMINI_API_KEY"],
                    "suggestions": "Your `.env` file or GEMINI_API_KEY environment variable is empty! I am providing this successful mock analysis so you can see the UI working while you set up your free key."
                }
            else:
                return Response({"error": f"AI Processing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        analysis = ResumeAnalysis.objects.create(
            resume_file=resume_file,
            job_description=job_description,
            ats_score=score,
            gap_analysis=gaps
        )

        return Response({
            "message": "Analysis successful.",
            "data": {
                "id": analysis.id,
                "ats_score": analysis.ats_score,
                "ats_match_level": match_level,
                "gap_analysis": analysis.gap_analysis,
                "resume_text": text
            }
        }, status=status.HTTP_200_OK)

class ChatbotView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        history = request.data.get("history", [])
        context_data = request.data.get("context", {})
        
        if not message:
            return Response({"error": "Message required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if not has_api_key():
                raise Exception("Missing API Key")

            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", max_tokens=400)
            
            sys_prompt = "You are an expert Resume Coach. Help the user improve their resume."
            if context_data:
                sys_prompt += f"\n\nContext from their recent resume scan:\nTarget Job: {context_data.get('job_desc', 'N/A')}\nATS Match Level: {context_data.get('ats_match_level', 'Unknown')}\nATS Score: {context_data.get('ats_score', 'N/A')}/100\nMissing Keywords: {context_data.get('gap_analysis', {}).get('missing_keywords', [])}\nSuggestions: {context_data.get('gap_analysis', {}).get('suggestions', 'None')}\n\n[USER RESUME CONTENT]:\n{context_data.get('resume_text', 'No resume text provided.')}"

            messages = [SystemMessage(content=sys_prompt)]
            for msg in history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content")))
                else:
                    messages.append(AIMessage(content=msg.get("content")))
                    
            messages.append(HumanMessage(content=message))
            
            response = llm.invoke(messages)
            return Response({"response": response.content}, status=status.HTTP_200_OK)
        except Exception as e:
            error_str = str(e).lower()
            if "key" in error_str or "auth" in error_str or "credentials" in error_str:
                return Response({"response": "I am currently running in Offline (Mock) mode because no GEMINI_API_KEY was found! Grab a free key from Google AI Studio and put it in your `.env` file to unlock my real AI brain!"}, status=status.HTTP_200_OK)
            return Response({"error": f"Chat LLM failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
