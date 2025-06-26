import flet as ft
import re
import asyncio
from database.mongodb_client import MongoDB
from database.session_manager import SessionManager

def signup_page(page: ft.Page, navigate_to):
    page.title = "Sign Up"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    db = MongoDB()
    session_manager = SessionManager()
    
    # If user is already logged in, redirect to home
    if session_manager.is_logged_in():
        navigate_to("/")
        return
    
    name_field = ft.TextField(
        label="Full Name",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        text_size=14,
        hint_text="Enter your full name",
        prefix_icon=ft.Icons.PERSON
    )
    
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
    
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        border=ft.InputBorder.UNDERLINE,
        width=300,
        password=True,
        can_reveal_password=True,
        text_size=14,
        hint_text="Confirm your password",
        prefix_icon=ft.Icons.LOCK_CLOCK
    )
    
    error_text = ft.Text(
        color=ft.Colors.RED_500,
        size=14,
        visible=False
    )
    
    success_container = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    name=ft.Icons.CHECK_CIRCLE,
                    color=ft.Colors.GREEN,
                    size=40
                ),
                ft.Text(
                    "Account created successfully!",
                    size=16,
                    color=ft.Colors.GREEN,
                    weight=ft.FontWeight.BOLD
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        visible=False
    )
    
    loading_container = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Creating your account...", size=14)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        visible=False
    )
    
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def validate_password(password):
        if len(password) < 8:
            return "Password must be at least 8 characters long"
        return None
    
    async def handle_signup(e):
        error_text.visible = False
        success_container.visible = False
        
        # Validate all fields
        if not all([name_field.value, email_field.value, password_field.value, confirm_password_field.value]):
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return
        
        if not validate_email(email_field.value):
            error_text.value = "Please enter a valid email"
            error_text.visible = True
            page.update()
            return
        
        password_error = validate_password(password_field.value)
        if password_error:
            error_text.value = password_error
            error_text.visible = True
            page.update()
            return
        
        if password_field.value != confirm_password_field.value:
            error_text.value = "Passwords do not match"
            error_text.visible = True
            page.update()
            return
        
        loading_container.visible = True
        signup_button.disabled = True
        page.update()
        
        try:
            user_id = db.create_user(
                email_field.value,
                password_field.value,
                name_field.value
            )
            
            if user_id:
                success_container.visible = True
                loading_container.visible = False
                page.update()
                
                await asyncio.sleep(2)
                result = db.authenticate_user(email_field.value, password_field.value)
                if result:
                    # Create session with user data
                    session = session_manager.create_session(result)
                    print(f"Created session during signup: {session}")
                    # Force reload to ensure session is saved properly
                    await asyncio.sleep(0.5)
                    navigate_to("/")
                else:
                    navigate_to("/login")
                
        except ValueError as ve:
            error_text.value = str(ve)
            error_text.visible = True
        except Exception as e:
            error_text.value = f"Sign up failed: {str(e)}"
            error_text.visible = True
        
        finally:
            loading_container.visible = False
            signup_button.disabled = False
            page.update()
    def handle_login_click(e):
        navigate_to("/login")
    
    signup_button = ft.ElevatedButton(
        "Sign Up",
        width=300,
        height=44,
        on_click=lambda e: asyncio.run(handle_signup(e)),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        ),
    )
    
    login_text = ft.TextButton(
        "Already have an account? Login",
        on_click=handle_login_click
    )
    
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Create Account",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        "Sign up to get started",
                        size=16,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=40),
                    name_field,
                    email_field,
                    password_field,
                    confirm_password_field,
                    error_text,
                    loading_container,
                    success_container,
                    signup_button,
                    login_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    )