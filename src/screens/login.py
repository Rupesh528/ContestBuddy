import flet as ft
from database.mongodb_client import MongoDB
from database.session_manager import SessionManager

def login_page(page: ft.Page, navigate_to):
    page.title = "Login"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    db = MongoDB()
    session_manager = SessionManager()
    
    # If user is already logged in, redirect to home
    if session_manager.is_logged_in():
        navigate_to("/")
        return
    
    email_field = ft.TextField(
        label="Email",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        text_size=14,
        hint_text="Enter your email",
        prefix_icon=ft.Icons.EMAIL
    )
    
    password_field = ft.TextField(
        label="Password",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        password=True,
        can_reveal_password=True,
        text_size=14,
        hint_text="Enter your password",
        prefix_icon=ft.Icons.LOCK
    )
    
    error_text = ft.Text(
        color=ft.Colors.RED_500,
        size=14,
        visible=False
    )
    
    loading_indicator = ft.ProgressRing(
        width=16,
        height=16,
        stroke_width=2,
        visible=False
    )
    
    def handle_login(e):
        error_text.visible = False
        
        if not email_field.value or not password_field.value:
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return
        
        # Show loading indicator
        loading_indicator.visible = True
        login_button.disabled = True
        page.update()
            
        try:
            # Add debug print statements
            print(f"Attempting to authenticate user: {email_field.value}")
            result = db.authenticate_user(email_field.value, password_field.value)
            print(f"Authentication result: {result}")
            
            if result:
                # Create session
                print("Creating session with user data")
                session = session_manager.create_session(result)
                print(f"Session created: {session}")
                
                                    # Verify the session before navigating
                if session:
                    print("Session verified, navigating to home")
                    # Make sure the session is correctly saved before navigation
                    session_manager._save_session(session)
                    # Small delay to ensure session is properly saved
                    page.update()
                    # Use a direct navigation without delay
                    page.go("/")
                else:
                    print("Session creation failed")
                    error_text.value = "Session creation failed. Please try again."
                    error_text.visible = True
            else:
                print("Authentication failed - invalid credentials")
                error_text.value = "Invalid email or password"
                error_text.visible = True
        except Exception as e:
            print(f"Login error: {str(e)}")
            error_text.value = f"Login failed: {str(e)}"
            error_text.visible = True
        
        # Hide loading indicator
        loading_indicator.visible = False
        login_button.disabled = False
        page.update()
    
    def handle_signup_click(e):
        navigate_to("/signup")
    
    login_button = ft.ElevatedButton(
        "Login",
        width=300,
        height=44,
        on_click=handle_login,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        ),
    )
    
    signup_text = ft.TextButton(
        "Don't have an account? Sign up",
        on_click=handle_signup_click
    )
    
    page.controls.clear()
    
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome Back!",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        "Sign in to continue",
                        size=16,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=40),
                    email_field,
                    password_field,
                    error_text,
                    ft.Row(
                        [login_button, loading_indicator],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    signup_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    )