import reflex as rx
from .state import AppState

class GoogleOAuthProvider(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleOAuthProvider"
    clientId: rx.Var[str]

class GoogleLogin(rx.Component):
    library = "@react-oauth/google"
    tag = "GoogleLogin"
    on_success: rx.EventHandler[lambda res: [res]]
    on_error: rx.EventHandler[lambda: []]

google_oauth_provider = GoogleOAuthProvider.create
google_login = GoogleLogin.create

def login_form():
    return rx.center(
        rx.vstack(
            rx.heading("Resume Coach", size="9", weight="bold", color_scheme="teal", letter_spacing="-0.05em"),
            rx.text("Supercharge your career with AI.", size="5", color="gray", margin_bottom="6"),
            
            rx.card(
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Sign In", value="login", width="50%"),
                        rx.tabs.trigger("Register", value="register", width="50%"),
                        width="100%",
                        margin_bottom="4"
                    ),
                    
                    rx.tabs.content(
                        rx.vstack(
                            rx.form(
                                rx.vstack(
                                    rx.input(placeholder="Email", name="email", type="email", required=True, size="3"),
                                    rx.input(placeholder="Password", name="password", type="password", required=True, size="3"),
                                    rx.button("Sign In securely", type="submit", width="100%", size="3", color_scheme="teal"),
                                    spacing="3", width="100%"
                                ),
                                on_submit=AppState.login, width="100%"
                            ),
                            rx.divider(margin_y="3"),
                            
                            rx.box(
                                google_oauth_provider(
                                    google_login(
                                        on_success=AppState.handle_google_auth,
                                        on_error=AppState.google_oauth_error
                                    ),
                                    clientId="541990120066-u0ifhuki32pdpddv5dsklh3tqvq96qta.apps.googleusercontent.com"
                                ),
                                width="100%",
                                display="flex",
                                justify_content="center"
                            ),
                            
                            rx.divider(margin_y="3"),
                            rx.button("Try as Guest", on_click=AppState.login_guest, variant="ghost", color_scheme="gray", width="100%", size="3"),
                            
                            spacing="2", width="100%"
                        ),
                        value="login"
                    ),
                    
                    rx.tabs.content(
                        rx.vstack(
                            rx.form(
                                rx.vstack(
                                    rx.input(placeholder="Full Name", name="name", required=True, size="3"),
                                    rx.input(placeholder="Email", name="email", type="email", required=True, size="3"),
                                    rx.input(placeholder="Password", name="password", type="password", required=True, size="3"),
                                    rx.button("Create Free Account", type="submit", width="100%", size="3", color_scheme="teal"),
                                    spacing="3", width="100%"
                                ),
                                on_submit=AppState.register, width="100%"
                            ),
                            width="100%"
                        ),
                        value="register"
                    ),
                    
                    default_value="login",
                    width="100%"
                ),
                size="4", 
                width="400px", 
                background="var(--gray-2)", 
                border_radius="xl",
                box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.4)",
                padding="6"
            ),
            align_items="center",
            spacing="4"
        ),
        width="100vw",
        height="100vh",
        background="#F4F4F5"
    )

def chat_bubble(msg):
    return rx.box(
        rx.cond(
            msg["role"] == "user",
            rx.box(rx.text(msg["content"], size="3", color="white"), bg="var(--blue-9)", padding="3", border_radius="1rem 1rem 0 1rem", max_width="80%", align_self="flex-end", box_shadow="0 2px 4px rgba(0,0,0,0.1)"),
            rx.box(rx.text(msg["content"], size="3", color="var(--gray-12)"), bg="#FFFFFF", border="1px solid var(--gray-4)", padding="3", border_radius="1rem 1rem 1rem 0", max_width="80%", align_self="flex-start", box_shadow="0 2px 4px rgba(0,0,0,0.05)")
        ),
        width="100%",
        display="flex",
        flex_direction="column",
        margin_bottom="3"
    )

def dashboard():
    return rx.hstack(
        # SIDEBAR PORTAL
        rx.cond(
            AppState.is_logged_in,
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.icon("layout-dashboard", size=24, color="var(--blue-9)"),
                        rx.vstack(
                            rx.heading("Your History", size="5", color="var(--gray-12)"),
                            rx.text(f"Welcome back, {AppState.user_name}!", size="2", color="var(--gray-11)", weight="medium"),
                            spacing="0"
                        ),
                        align_items="center",
                        spacing="3"
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("log-out", size=18), 
                        "Exit",
                        on_click=AppState.logout, 
                        variant="soft", 
                        color_scheme="red", 
                        size="2",
                        cursor="pointer"
                    ),
                    width="100%",
                    align_items="center",
                    padding_bottom="4"
                ),
                rx.divider(border_color="var(--gray-5)"),
                rx.vstack(
                    rx.foreach(
                        AppState.user_history,
                        lambda h: rx.card(
                            rx.vstack(
                                rx.text(h["job"], weight="bold", size="2", color="var(--gray-12)"),
                                rx.hstack(
                                    rx.badge(f"Score: {h['ats_score']}", color_scheme="blue", variant="surface"),
                                    rx.text(h["date"], size="1", color="var(--gray-10)"),
                                    justify_content="space-between",
                                    width="100%"
                                )
                            ),
                            width="100%",
                            background="#FFFFFF",
                            border="1px solid var(--gray-4)",
                            box_shadow="0 1px 3px rgba(0,0,0,0.05)",
                            on_click=lambda: AppState.load_history(h["id"]),
                            transition="all 0.15s ease-in-out",
                            _hover={"background": "var(--gray-2)", "cursor": "pointer", "border_color": "var(--blue-7)"}
                        )
                    ),
                    spacing="3",
                    margin_top="4"
                ),
                width="320px",
                height="100vh",
                background="#FAFAFA",
                border_right="1px solid var(--gray-5)",
                padding="6",
            ),
            rx.box(display="none")
        ),
        # PRIMARY PORTAL
        rx.scroll_area(
            rx.vstack(
                rx.box(
                    rx.heading("ATS Match Analyzer", size="9", margin_top="8", weight="bold", color="var(--gray-12)", letter_spacing="-0.03em"),
                    rx.text("Upload your resume and paste the Job Description below to evaluate your compatibility.", size="4", color="var(--gray-10)", margin_top="2"),
                    text_align="center",
                    width="100%"
                ),
                
                rx.card(
                    rx.vstack(
                        rx.flex(
                            rx.upload(
                                rx.vstack(
                                    rx.icon("cloud-upload", size=32, color="var(--blue-9)"),
                                    rx.button("Select PDF File", variant="soft", color_scheme="blue", size="2", cursor="pointer"),
                                    rx.text(rx.cond(AppState.resume_filename != "", AppState.resume_filename, "Drag and drop your PDF here"), size="2", color="var(--gray-9)"),
                                    align_items="center",
                                    spacing="2"
                                ),
                                id="upload",
                                padding="3em",
                                border="2px dashed var(--gray-5)",
                                border_radius="1rem",
                                width="100%",
                                background="#FFFFFF",
                                transition="all 0.2s ease",
                                _hover={"background": "var(--blue-2)", "border_color": "var(--blue-8)"}
                            ),
                            rx.text_area(placeholder="Paste Job Description here...", on_blur=AppState.set_job_desc, width="100%", height="170px", size="3", background="#FFFFFF", border="1px solid var(--gray-5)", _hover={"border_color":"var(--blue-7)"}),
                            width="100%",
                            direction="row",
                            spacing="4"
                        ),
                        rx.button(
                            "Evaluate Match against ATS", 
                            on_click=AppState.handle_upload(rx.upload_files(upload_id="upload")),
                            color_scheme="blue", size="4", width="100%", loading=AppState.evaluate_loading,
                            box_shadow="0 4px 12px rgba(0, 112, 243, 0.2)",
                            border_radius="full",
                            variant="solid",
                            _hover={"box_shadow": "0 6px 16px rgba(0, 112, 243, 0.3)", "transform": "translateY(-1px)"},
                            transition="all 0.2s ease"
                        ),
                        spacing="6",
                        width="100%"
                    ),
                    width="100%",
                    padding="8",
                    background="#FFFFFF",
                    border="1px solid var(--gray-4)",
                    border_radius="2xl",
                    box_shadow="0 10px 30px -10px rgba(0, 0, 0, 0.05)",
                    margin_top="6"
                ),
                
                # RESULTS PORTAL
                rx.cond(
                     AppState.has_results,
                     rx.card(
                         rx.vstack(
                            rx.hstack(
                                rx.icon("zap", size=32, color="var(--blue-9)"),
                                rx.heading(f"Score: {AppState.ats_score}/100 - {AppState.ats_match_level}", size="8", color="var(--gray-12)"),
                                align_items="center"
                            ),
                            rx.divider(margin_y="3", border_color="var(--gray-4)"),
                            rx.heading("Gaps Identified:", size="4", color="var(--gray-11)"),
                            rx.text(rx.cond(AppState.missing_keywords.length() > 0, AppState.missing_keywords.join(", "), "None"), size="3", weight="medium", color="var(--blue-9)"),
                            rx.text(AppState.suggestions, size="3", color="var(--gray-11)", line_height="1.6"),
                            width="100%"
                         ),
                         width="100%",
                         background="linear-gradient(135deg, #FFFFFF 0%, #FAFAFA 100%)",
                         border="1px solid var(--gray-4)",
                         border_radius="2xl",
                         padding="8",
                         margin_top="8",
                         box_shadow="0 10px 30px -10px rgba(0, 0, 0, 0.08)"
                     ),
                     rx.box()
                ),

                # CHATBOT COMPONENT
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("bot", size=24, color="var(--blue-9)"),
                            rx.heading("Resume Coach Chatbot", size="5", color="var(--gray-12)"),
                            align_items="center"
                        ),
                        rx.divider(margin_y="3", border_color="var(--gray-4)"),
                        
                        rx.cond(
                            AppState.is_guest,
                            rx.callout("CHAT IS LOCKED. You must log in to unlock the Resume Coach functionality.", color_scheme="red", icon="lock_keyhole", width="100%", variant="soft"),
                            rx.vstack(
                                rx.box(
                                    rx.foreach(AppState.chat_history, chat_bubble),
                                    rx.cond(AppState.chat_history.length() == 0, rx.text("Start your interview prep here!", align="center", color="var(--gray-8)", margin_top="4")),
                                    height="350px",
                                    overflow_y="auto",
                                    padding="4",
                                    width="100%",
                                    background="#FAFAFA",
                                    border_radius="xl",
                                    border="1px solid var(--gray-4)",
                                ),
                                rx.hstack(
                                    rx.input(placeholder="Ask for precise resume feedback...", value=AppState.current_chat, on_change=AppState.set_current_chat, width="100%", size="3", background="#FFFFFF", border_color="var(--gray-5)"),
                                    rx.button(rx.icon("send", size=18), "Send", on_click=AppState.send_chat, color_scheme="blue", size="3", border_radius="lg"),
                                    width="100%"
                                ),
                                width="100%"
                            )
                        ),
                        width="100%"
                    ),
                    width="100%",
                    margin_top="8",
                    margin_bottom="10",
                    padding="6",
                    background="#FFFFFF",
                    border="1px solid var(--gray-4)",
                    border_radius="2xl",
                    box_shadow="0 10px 40px -10px rgba(0,0,0,0.05)"
                ),
                
                padding_x="8",
                width="100%",
                max_width="1200px",
                align_self="center",
            ),
            width="100%",
        ),
        spacing="0",
        width="100vw",
        height="100vh",
        background="#F4F4F5",
        color="var(--gray-12)"
    )

def index():
    return rx.cond(
        AppState.is_logged_in | AppState.is_guest,
        dashboard(),
        login_form()
    )

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue"
    )
)
app.add_page(index, title="Premium ATS Coach", on_load=AppState.handle_page_load)
