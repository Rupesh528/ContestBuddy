import flet as ft
from database.mongodb_client import MongoDB
from database.session_manager import SessionManager
from components.logout_component import logout_button
from services.reminder_service import ensure_reminder_monitor_running


def home_page(page: ft.Page, navigate_to):
    page.title = "🏠 Home - Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    session_manager = SessionManager()
    current_user = session_manager.get_current_user()
    ensure_reminder_monitor_running()    
    print(f"Home page: current user = {current_user}")
    
    # If user is not logged in, redirect to login
    if not current_user:
        print("No user session found, redirecting to login")
        navigate_to("/login")
        return
    
    # Header with greeting
    greeting_text = f"Welcome back, {current_user.get('name', 'User')}!"
    
    header = ft.Column([
        ft.Text(
            greeting_text,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        ),
        
    ])

    # Quick stats row
    stats_row = ft.Row(
        [
           
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND
    )

    # Button ListView
    button_list = ft.ListView(
        expand=1,
        spacing=15,
        padding=20,
        auto_scroll=False
    )

    button_list.controls.extend([
        ft.ElevatedButton(
            text="📅 Upcoming Contests",
            on_click=lambda _: navigate_to("/contests"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)
        ),
        ft.ElevatedButton(
            text="⏰ Reminders",
            on_click=lambda _: navigate_to("/reminders"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_500, color=ft.Colors.WHITE)
        ),
        ft.ElevatedButton(
            text="🔍 Profile Analyzer",
            on_click=lambda _: navigate_to("/profile-analyzer"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL_500, color=ft.Colors.WHITE)
         ),
        ft.ElevatedButton(
            text="👤 Profile",
            on_click=lambda _: navigate_to("/profile"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_500, color=ft.Colors.WHITE)
        ),
    
        ft.ElevatedButton(
            text="📚 CP-guide",
            on_click=lambda _: navigate_to("/cp-guide"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        ),
            ft.ElevatedButton(
            text="⚙️ Settings",
            on_click=lambda _: navigate_to("/settings"),
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_700, color=ft.Colors.WHITE)
        ),
    ])
    

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    header,
    
                    ft.Text("Quick Access", size=16, weight=ft.FontWeight.BOLD),
                    button_list,
    
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=ft.padding.all(20),
            expand=True
        )
    )

    page.update()