import streamlit as st
import requests
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="ATS Resume Evaluator", page_icon="📄", layout="wide")

st.title("📄 ATS Resume Evaluator & AI Assistant")
st.markdown("Upload your resume and provide a Job Description to get an ATS Match score and tailored feedback!")

# Active FastAPI Backend URL
API_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8080/api/")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your PDF resume", type=["pdf"])

with col2:
    st.subheader("2. Target Job Description")
    job_desc = st.text_area("Paste the Job Description here...", height=150)

if st.button("Evaluate Match against ATS", type="primary", use_container_width=True):
    if uploaded_file and job_desc:
        with st.spinner("Analyzing resume against the Job Description using Vertex AI..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"job_description": job_desc}
                res = requests.post(f"{API_URL}analyze/", files=files, data=data)
                
                if res.status_code == 200:
                    result_data = res.json().get("data", {})
                    st.success("✅ Analysis Complete!")
                    
                    st.session_state.messages = [] # Reset chat limits for the new file!
                    
                    # Save context memory for the chatbot!
                    gaps = result_data.get("gap_analysis", {})
                    st.session_state.ats_context = {
                        "job_desc": job_desc,
                        "ats_match_level": result_data.get('ats_match_level'),
                        "ats_score": result_data.get('ats_score'),
                        "gap_analysis": gaps,
                        "resume_text": result_data.get("resume_text", "")
                    }
                else:
                    st.error(f"Backend Error: {res.text}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

    else:
        st.warning("Please upload a PDF resume to start.")

# Keep the ATS Analysis pinned to the screen permanently!
if "ats_context" in st.session_state:
    ctx = st.session_state.ats_context
    st.divider()
    st.subheader(f"📊 ATS Match Result: **{ctx.get('ats_match_level', 'Unknown')}** ({ctx.get('ats_score', 'N/A')}/100)")
    st.subheader("🔍 Gap Analysis")
    gaps = ctx.get("gap_analysis", {})
    if gaps:
        st.write(f"**Missing Keywords:** {', '.join(gaps.get('missing_keywords', []))}")
        st.write(f"**Suggestions:** {gaps.get('suggestions', '')}")

st.divider()

# --- CHATBOT SECTION ---
st.subheader("💬 Resume Coach")
st.caption("Ask questions about how to improve your resume based on the gaps identified!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

MAX_PROMPTS = 3
user_msg_count = sum(1 for msg in st.session_state.messages if msg["role"] == "user")

if user_msg_count >= MAX_PROMPTS:
    st.info("🔒 **Session Limit Reached:** You have completed your 3 free consultation questions! Please hit **Evaluate Match against ATS** or upload a new resume to start a fresh session.")
    prompt = st.chat_input("Limit reached.", disabled=True)
else:
    prompt = st.chat_input(f"E.g., How can I fix the missing Vector Databases gap? ({MAX_PROMPTS - user_msg_count} remaining)")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send the current prompt, prior history, and ATS context
                payload = {
                    "message": prompt, 
                    "history": st.session_state.messages[:-1],
                    "context": st.session_state.get("ats_context", {})
                }
                res = requests.post(f"{API_URL}chat/", json=payload)
                
                if res.status_code == 200:
                    response = res.json().get("response", "No response from AI.")
                else:
                    response = f"Backend Error: {res.text}"
            except Exception as e:
                response = f"Connection failed: {str(e)}"
                
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
