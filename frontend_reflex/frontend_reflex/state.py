import reflex as rx
import requests

API_URL = "http://localhost:8080/api/"

class AppState(rx.State):
    # Auth
    user: dict = {}
    is_guest: bool = False
    
    # Input params
    job_desc: str = ""
    resume_filename: str = ""
    
    # Evaluation Results
    evaluate_loading: bool = False
    ats_score: str = ""
    ats_match_level: str = ""
    missing_keywords: list[str] = []
    suggestions: str = ""
    resume_text: str = ""
    
    # History
    chat_history: list[dict[str, str]] = []
    user_history: list[dict[str, str]] = []
    current_chat: str = ""
    
    @rx.var
    def is_logged_in(self) -> bool:
        return "id" in self.user
        
    @rx.var
    def user_name(self) -> str:
        return str(self.user.get("name", "User")).split(" ")[0] if self.is_logged_in else "Guest"
        
    @rx.var
    def has_results(self) -> bool:
        return self.ats_score != ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files: 
            yield rx.window_alert("Please select a PDF resume file first!")
            return
            
        file = files[0]
        upload_data = await file.read()
        self.resume_filename = file.filename
        
        self.evaluate_loading = True
        yield
        
        files_payload = {"file": (file.filename, upload_data, "application/pdf")}
        data = {"job_description": self.job_desc}
        if self.is_logged_in:
            data["user_id"] = str(self.user.get("id"))
            
        try:
            res = requests.post(API_URL + "analyze/", files=files_payload, data=data)
            self.evaluate_loading = False
            
            if res.status_code == 200:
                rj = res.json()
                ans = rj.get("data", {})
                self.ats_score = ans.get("ats_score", "")
                self.ats_match_level = ans.get("ats_match_level", "")
                self.resume_text = ans.get("resume_text", "")
                gaps = ans.get("gap_analysis", {})
                self.missing_keywords = gaps.get("missing_keywords", [])
                self.suggestions = gaps.get("suggestions", "")
                self.chat_history = []
                if self.is_logged_in:
                    self.fetch_history()
            else:
                yield rx.window_alert(f"Error reaching backend: {res.text}")
        except Exception as e:
            self.evaluate_loading = False
            yield rx.window_alert(f"Backend offline: {str(e)}")
            
    def set_job_desc(self, text):
        self.job_desc = text

    def register(self, form_data: dict):
        email, name, password = form_data.get("email"), form_data.get("name"), form_data.get("password")
        try:
            res = requests.post(API_URL + "register/", json={"email": email, "name": name, "password": password})
            if res.status_code == 200:
                data = res.json()
                self.user = data["user"]
                self.is_guest = False
                self.fetch_history()
            else:
                return rx.window_alert(f"Registration Failed! Database responded: {res.text}")
        except Exception as e:
            return rx.window_alert(f"Connection Failed! Did you start Uvicorn? Error: {str(e)}")

    def login(self, form_data: dict):
        email, password = form_data.get("email"), form_data.get("password")
        try:
            res = requests.post(API_URL + "login/", json={"email": email, "password": password, "is_oauth": False})
            if res.status_code == 200:
                data = res.json()
                self.user = data["user"]
                self.is_guest = False
                self.fetch_history()
            else:
                return rx.window_alert(f"Login Rejected! Backend Error: {res.text}")
        except Exception as e:
            return rx.window_alert(f"Connection Failed! Is your FastAPI running on uvicorn? Error: {str(e)}")

    def handle_google_auth(self, response: dict):
        try:
            res = requests.post(API_URL + "google-login/", json={"credential": response.get("credential")})
            if res.status_code == 200:
                data = res.json()
                self.user = data["user"]
                self.is_guest = False
                self.fetch_history()
            else:
                return rx.window_alert(f"Google Login Blocked: {res.text}")
        except Exception as e:
            return rx.window_alert(f"Connection Failed: {str(e)}")
            
    def google_oauth_error(self):
        return rx.window_alert("Google Sign-In dropped unexpectedly.")

    def login_guest(self):
        self.is_guest = True
        self.user = {}

    def fetch_history(self):
        if self.is_logged_in:
            res = requests.get(f"{API_URL}user/{self.user['id']}/history/")
            if res.status_code == 200:
                self.user_history = res.json().get("history", [])

    # Evaluation is now natively merged into handle_upload

    def load_history(self, history_id: int):
        self.evaluate_loading = True
        yield
        try:
            res = requests.get(f"{API_URL}history/{history_id}")
            self.evaluate_loading = False
            if res.status_code == 200:
                data = res.json()
                self.job_desc = data.get("job_description", "")
                self.ats_score = data.get("ats_score", "")
                self.ats_match_level = data.get("ats_match_level", "")
                self.resume_text = data.get("resume_text", "")
                gaps = data.get("gap_analysis", {}) or {}
                self.missing_keywords = gaps.get("missing_keywords", [])
                self.suggestions = gaps.get("suggestions", "")
                self.chat_history = []
                self.resume_filename = f"Auto-loaded: Analysis Archive #{history_id}"
            else:
                yield rx.window_alert("Failed to pull history record.")
        except Exception as e:
            self.evaluate_loading = False
            yield rx.window_alert(f"Connection Error: {str(e)}")

    def set_current_chat(self, text):
        self.current_chat = text

    def logout(self):
        self.reset()

    def handle_page_load(self):
        self.reset()

    def send_chat(self):
        if self.is_guest:
            return rx.window_alert("You must be signed in to use the Chatbot!")
            
        q = self.current_chat
        self.current_chat = ""
        self.chat_history.append({"role": "user", "content": q})
        yield
        
        ctx = {
            "job_desc": self.job_desc,
            "ats_score": self.ats_score,
            "ats_match_level": self.ats_match_level,
            "gap_analysis": {"missing_keywords": self.missing_keywords, "suggestions": self.suggestions},
            "resume_text": self.resume_text
        }
        res = requests.post(API_URL + "chat/", json={
            "user_id": str(self.user["id"]),
            "message": q,
            "history": [c for c in self.chat_history][:-1],
            "context": ctx
        })
        
        if res.status_code == 200:
            self.chat_history.append({"role": "ai", "content": res.json().get("response")})
        else:
            self.chat_history.append({"role": "ai", "content": "Error or locked out. Guests cannot chat."})
