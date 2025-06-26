import flet as ft
import json
import os
from database.session_manager import SessionManager

def profile_page(page: ft.Page, navigate_to):
    page.title = "Profile"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    session_manager = SessionManager()
    
    # Check if user is logged in
    current_user = session_manager.get_current_user()
    if not current_user:
        navigate_to("/login")
        return

    # Get user data
    user_name = current_user.get("name", "User")
    user_email = current_user.get("email", "")
    
    # Load saved platform usernames
    saved_usernames = {}
    preferences_file = "user_preferences.json"
    if os.path.exists(preferences_file):
        try:
            with open(preferences_file, 'r') as f:
                saved_usernames = json.load(f)
        except:
            saved_usernames = {}
    
    # Create profile banner
    profile_banner = ft.Container(
        width=page.width,
        height=150,
        bgcolor=ft.colors.BLUE_700,
        border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
        padding=ft.padding.all(20),
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(
                        name=ft.icons.ACCOUNT_CIRCLE,
                        size=60,
                        color=ft.colors.WHITE
                    ),
                    alignment=ft.alignment.center
                ),
                ft.Text(
                    user_name,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    user_email,
                    size=14,
                    color=ft.colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )
    )
    
    # Platform usernames section
    platform_usernames_section = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Platform Usernames",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                ft.Text(
                    "Set your usernames for different competitive programming platforms",
                    size=14,
                    color=ft.colors.GREY_800
                )
            ],
            spacing=5
        ),
        margin=ft.margin.only(left=20, top=20, right=20, bottom=10)
    )
    
    # Status text for save operation
    save_status = ft.Text(
        "",
        size=14,
        color=ft.colors.GREEN_700,
        visible=False
    )
    
    # Create textfields for each platform
    codeforces_username = ft.TextField(
        label="Codeforces Username",
        hint_text="Enter your Codeforces handle",
        prefix_icon=ft.icons.CODE,
        value=saved_usernames.get("codeforces_username", ""),
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        expand=True
    )
    
    leetcode_username = ft.TextField(
        label="LeetCode Username",
        hint_text="Enter your LeetCode handle",
        prefix_icon=ft.icons.CODE,
        value=saved_usernames.get("leetcode_username", ""),
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        expand=True
    )
    
    codechef_username = ft.TextField(
        label="CodeChef Username",
        hint_text="Enter your CodeChef handle",
        prefix_icon=ft.icons.CODE,
        value=saved_usernames.get("codechef_username", ""),
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        expand=True
    )
    
    atcoder_username = ft.TextField(
        label="AtCoder Username",
        hint_text="Enter your AtCoder handle",
        prefix_icon=ft.icons.CODE,
        value=saved_usernames.get("atcoder_username", ""),
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        expand=True
    )
    
    def save_platforms(e):
        # Save platform usernames to preferences file
        preferences = {
            "codeforces_username": codeforces_username.value.strip(),
            "leetcode_username": leetcode_username.value.strip(),
            "codechef_username": codechef_username.value.strip(),
            "atcoder_username": atcoder_username.value.strip()
        }
        
        try:
            with open("user_preferences.json", 'w') as f:
                json.dump(preferences, f)
            
            save_status.value = "✅ Platform usernames saved successfully"
            save_status.color = ft.colors.GREEN_700
            save_status.visible = True
        except Exception as e:
            save_status.value = f"❌ Error saving preferences: {str(e)}"
            save_status.color = ft.colors.RED_700
            save_status.visible = True
        
        page.update()
        
        # Hide success message after 3 seconds
        def hide_status():
            save_status.visible = False
            page.update()
        
        page.after(3, hide_status)
        
    save_button = ft.ElevatedButton(
        "Save Platform Usernames",
        icon=ft.icons.SAVE,
        on_click=save_platforms,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_700
        )
    )

    platform_fields = ft.Column(
        [
            codeforces_username,
            leetcode_username,
            codechef_username,
            atcoder_username,
            ft.Container(
                content=ft.Row(
                    [
                        save_button,
                        save_status
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                margin=ft.margin.only(top=10)
            )
        ],
        spacing=10
    )
    
    platform_card = ft.Card(
        content=ft.Container(
            content=platform_fields,
            padding=20,
            width=page.width
        ),
        margin=ft.margin.symmetric(horizontal=20)
    )
    
    # Function to handle logout
    def handle_logout(e):
        session_manager.logout()
        navigate_to("/login")
    
    # Logout button
    logout_button = ft.ElevatedButton(
        "Logout",
        icon=ft.icons.LOGOUT,
        on_click=handle_logout,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.RED_500
        )
    )
    
    # Create profile options
    profile_options = ft.ListView(
        spacing=10,
        padding=20,
        controls=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(name=ft.icons.SETTINGS, color=ft.colors.BLUE_700),
                        ft.Text("Settings", size=16)
                    ],
                    spacing=10
                ),
                on_click=lambda _: navigate_to("/settings"),
                padding=ft.padding.all(15),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(name=ft.icons.ANALYTICS, color=ft.colors.BLUE_700),
                        ft.Text("View Analytics", size=16)
                    ],
                    spacing=10
                ),
                on_click=lambda _: navigate_to("/analytics"),
                padding=ft.padding.all(15),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(name=ft.icons.NOTIFICATIONS, color=ft.colors.BLUE_700),
                        ft.Text("Manage Reminders", size=16)
                    ],
                    spacing=10
                ),
                on_click=lambda _: navigate_to("/reminders"),
                padding=ft.padding.all(15),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(name=ft.icons.ANALYTICS, color=ft.colors.BLUE_700),
                        ft.Text("Profile Analyzer", size=16)
                    ],
                    spacing=10
                ),
                on_click=lambda _: navigate_to("/profile-analyzer"),
                padding=ft.padding.all(15),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50
            ),
            ft.Container(
                content=logout_button,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20)
            )
        ]
    )
    
    # Add all elements to page
    page.controls.clear()
    page.add(
        ft.Column(
            [
                profile_banner,
                platform_usernames_section,
                platform_card,
                ft.Container(
                    content=ft.Text(
                        "Profile Options",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700
                    ),
                    margin=ft.margin.only(top=20, left=20)
                ),
                profile_options
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
    )
    
    page.update()