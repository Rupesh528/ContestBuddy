import flet as ft
from screens.home import home_page
from screens.contest_list import contest_list_page
from screens.reminders import reminders_page
from screens.profile import profile_page
from screens.profile_analyzer import profile_analyzer_page

from screens.login import login_page
from screens.signup import signup_page
from screens.settings import settings_page
from database.session_manager import SessionManager

from screens.cp_guide import cp_guide_page

def main(page: ft.Page):
    page.title = "Competitive Programming Reminder"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.padding.only(top=50)
 
    
    session_manager = SessionManager()

    # Protected routes that require authentication
    protected_routes = [
        "/", 
        "/contests", 
        "/reminders", 
        "/profile", 
        "/profile-analyzer", 
        "/analytics", 
        "/cp-guide",  # Add this
        "/settings"
    ]
        
    # Public routes that don't require authentication
    public_routes = [
        "/login", 
        "/signup"
    ]

    def navigate_to(route: str):
        print(f"Navigating to: {route}")
        page.go(route)

    def handle_navigation_bar_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            navigate_to("/")
        elif selected_index == 1:
            navigate_to("/reminders")
        elif selected_index == 2:
            navigate_to("/profile-analyzer")
        elif selected_index == 3:
            navigate_to("/profile")

    def is_authenticated():
        # Force reload the session data before checking
        session_manager.session_data = session_manager._load_session()
        auth_status = session_manager.is_logged_in()
        print(f"Authentication check: {auth_status}")
        return auth_status
    
    def show_user_status():
        # Add user status to app bar
        if is_authenticated():
            user = session_manager.get_current_user()
            user_name = user.get("name", "User")
            print(f"Showing app bar for user: {user_name}")
            
            # Create profile button in app bar
            page.appbar = ft.AppBar(
                title=ft.Text("Competitive Programming Reminder"),
                bgcolor=ft.colors.BLUE_700,
                actions=[
                    ft.PopupMenuButton(
                        icon=ft.icons.ACCOUNT_CIRCLE,
                        tooltip=f"Logged in as {user_name}",
                        items=[
                            ft.PopupMenuItem(
                                text=f"Signed in as {user_name}",
                                icon=ft.icons.PERSON,
                                disabled=True
                            ),
                            ft.PopupMenuItem(
                                text="Profile",
                                icon=ft.icons.ACCOUNT_CIRCLE,
                                on_click=lambda _: navigate_to("/profile")
                            ),
                            ft.PopupMenuItem(
                                text="Settings",
                                icon=ft.icons.SETTINGS,
                                on_click=lambda _: navigate_to("/settings")
                            ),
                            ft.PopupMenuItem(
                                text="Logout",
                                icon=ft.icons.LOGOUT,
                                on_click=lambda _: handle_logout()
                            ),
                        ]
                    )
                ]
            )
            page.update()
        else:
            print("No authenticated user, not showing app bar")
    
    def handle_logout():
        print("Logging out from main")
        session_manager.logout()
        navigate_to("/login")

    def route_change(route):
        print(f"Route changed to: {route}")
        page.controls.clear()
        
        current_route = route.route
        
        # Check if the route requires authentication
        if current_route in protected_routes and not is_authenticated():
            print(f"Route {current_route} requires authentication, redirecting to login")
            navigate_to("/login")
            return
        
        try:
            if current_route == "/login":
                page.navigation_bar.visible = False
                page.appbar = None
                login_page(page, navigate_to)
            elif current_route == "/signup":
                page.navigation_bar.visible = False
                page.appbar = None
                signup_page(page, navigate_to)
            elif current_route == "/" or current_route == "":
                page.navigation_bar.visible = True
                page.navigation_bar.selected_index = 0
                show_user_status()
                home_page(page, navigate_to)
            elif current_route == "/contests":
                page.navigation_bar.visible = True
                show_user_status()
                contest_list_page(page, navigate_to)
            elif current_route == "/reminders":
                page.navigation_bar.visible = True
                page.navigation_bar.selected_index = 1
                show_user_status()
                reminders_page(page, navigate_to)
            elif current_route == "/profile":
                page.navigation_bar.visible = True
                page.navigation_bar.selected_index = 3
                show_user_status()
                profile_page(page, navigate_to)
            elif current_route == "/profile-analyzer":
                page.navigation_bar.visible = True
                page.navigation_bar.selected_index = 2
                show_user_status()
                profile_analyzer_page(page, navigate_to)
            elif current_route == "/settings":
                page.navigation_bar.visible = True
                show_user_status()
                settings_page(page, navigate_to)
            elif current_route == "/cp-guide":  # Add this new route
                page.navigation_bar.visible = True
                show_user_status()
                cp_guide_page(page, navigate_to)
            else:
                page.add(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("404 - Page Not Found", size=32, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton("Go Home", on_click=lambda _: navigate_to("/"))
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    )
                )
        except Exception as e:
            print(f"Route change error: {str(e)}")
            navigate_to("/")
            
        page.update()

    page.on_route_change = route_change

    page.navigation_bar = ft.NavigationBar(
        visible=False,
        on_change=handle_navigation_bar_change,
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS, label="Reminders"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Analytics"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_CIRCLE, label="Profile"),
        ]
    )

    # Check if user is already logged in
    if is_authenticated():
        print("User already authenticated, navigating to home")
        navigate_to("/")
    else:
        # If not logged in, start with login page
        print("No authenticated user, navigating to login")
        navigate_to("/login")

if __name__ == "__main__":
    ft.app(target=main)