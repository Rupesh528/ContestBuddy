# settings.py
import flet as ft

def settings_page(page: ft.Page, navigate_to):
    page.title = "Settings"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def handle_logout(e):
        # Add logout logic here (clear session, etc.)
        navigate_to("/login")
    
    # Create AppBar
    app_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: navigate_to("/"),
                    icon_color=ft.Colors.BLUE_900,
                ),
                ft.Text(
                    "Settings", 
                    weight=ft.FontWeight.BOLD, 
                    size=20,
                    color=ft.Colors.BLUE_900,
                ),
            ],
            spacing=10
        ),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=ft.border_radius.only(
            bottom_left=10,
            bottom_right=10,
        ),
    )

    # Settings options
    theme_switch = ft.Switch(
        label="Dark Mode",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=lambda e: setattr(page, 'theme_mode', 
                                  ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT)
    )

    notifications_switch = ft.Switch(
        label="Contest Notifications",
        value=True
    )
    
    version_info = ft.Text(
        "Version 1.0.0",
        size=14,
        color=ft.Colors.GREY_700,
    )

    logout_button = ft.ElevatedButton(
        "Logout",
        icon=ft.icons.LOGOUT,
        on_click=handle_logout,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600
        ),
    )

    page.add(
        ft.Column([
            app_bar,
            ft.Container(
                content=ft.Column([
                    # Settings sections
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Appearance", 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD),
                            theme_switch,
                        ], spacing=10),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Notifications", 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD),
                            notifications_switch,
                        ], spacing=10),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Account", 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD),
                            logout_button,
                        ], spacing=10),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("About", 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD),
                            version_info,
                        ], spacing=10),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                    ),
                ], spacing=20),
                padding=20,
            ),
        ], spacing=0, expand=True)
    )
