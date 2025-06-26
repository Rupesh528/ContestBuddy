import flet as ft
from database.session_manager import SessionManager

def logout_button(navigate_to, text="Logout", icon=ft.icons.LOGOUT, width=None, height=None, color=ft.colors.RED_500):
    """Create a standardized logout button"""
    session_manager = SessionManager()
    
    def handle_logout(e):
        # Show a confirmation dialog
        def close_dialog(e):
            dialog.open = False
            page.update()
            
        def confirm_logout(e):
            close_dialog(e)
            print("Confirming logout")
            success = session_manager.logout()
            if success:
                print("Logout successful, redirecting to login page")
            else:
                print("Logout failed")
            navigate_to("/login")
        
        page = e.page
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Logout"),
            content=ft.Text("Are you sure you want to log out?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Logout", on_click=confirm_logout),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    # Create and return the button
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=handle_logout,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=color
        ),
        width=width,
        height=height
    )