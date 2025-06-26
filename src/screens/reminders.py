# screens/reminders.py
import flet as ft
import flet_permission_handler as fph
import json
import os
import threading
import time
from datetime import datetime
from services.reminder_service import (
    load_reminders, 
    remove_reminder, 
    request_notification_permission,
    ensure_reminder_monitor_running
)

def reminders_page(page: ft.Page, navigate_to):
    page.title = "Contest Reminders"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    
    # Global countdown update thread control
    countdown_running = True
    
    # Permission handler
    ph = fph.PermissionHandler()
    page.overlay.append(ph)
    
    # UI Components
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: navigate_to("/"),
                    icon_color=ft.Colors.BLUE_900,
                ),
                ft.Text(
                    "Contest Reminders",
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
    
    no_reminders_text = ft.Text(
        "You haven't set any reminders yet.",
        color=ft.Colors.GREY_700,
        size=16,
        visible=False
    )
    
    info_text = ft.Text(
        "We'll notify you 30 minutes before each contest starts.",
        size=14,
        color=ft.Colors.GREY_600,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Permission status text
    status_text = ft.Text(
        "Notification Permission Status Unknown...", 
        color=ft.Colors.GREY,
        size=12,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Permission buttons
    check_permission_button = ft.OutlinedButton(
        "Check Notification Permission",
        data=fph.PermissionType.NOTIFICATION,
        width=200,
    )
    
    request_permission_button = ft.OutlinedButton(
        "Request Notification Permission", 
        data=fph.PermissionType.NOTIFICATION,
        width=200,
    )
    
    # Test notification button
    test_notification_button = ft.ElevatedButton(
        "Send Test Notification",
        disabled=True,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_700,
        ),
        width=200,
        height=45,
    )
    
    reminder_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=False
    )
    
    def check_permission(e):
        result = ph.check_permission(e.control.data)
        status_text.value = f"Permission Check: {e.control.data.name} - {result}"
        test_notification_button.disabled = not result
        status_text.color = ft.Colors.GREEN if result else ft.Colors.RED
        page.update()

    def request_permission(e):
        result = ph.request_permission(e.control.data)
        result_two = ph.request_permission(fph.PermissionType.ACCESS_NOTIFICATION_POLICY)
        status_text.value = f"Permission requested: {e.control.data.name} - {result}"
        test_notification_button.disabled = not result
        status_text.color = ft.Colors.GREEN if result else ft.Colors.RED
        page.update()
    
    def send_test_notification(e):
        from services.reminder_service import send_notification
        title = "🏆 Test Notification"
        text = "This is a test notification from Contest Reminder App"
        success = send_notification(title, text)
        
        if success:
            status_text.value = "✅ Test notification sent successfully."
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = "❗ Failed to send test notification."
            status_text.color = ft.Colors.RED
        page.update()
    
    # Connect event handlers
    check_permission_button.on_click = check_permission
    request_permission_button.on_click = request_permission
    test_notification_button.on_click = send_test_notification
    
    def parse_datetime_string(datetime_str):
        """Parse datetime string to datetime object."""
        try:
            # Extract the date and time part (excluding IST)
            dt_part = datetime_str.split(" IST")[0]
            # Parse datetime with specific format
            return datetime.strptime(dt_part, "%Y-%m-%d %I:%M %p")
        except ValueError:
            return None
    
    def format_countdown(seconds):
        """Format seconds into readable countdown format."""
        if seconds <= 0:
            return "🔔 Notification Time!"
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        else:
            return f"{minutes}m {secs}s"
    
    def create_reminder_item(reminder_id, reminder_data):
        """Create a reminder list item with countdown."""
        event_name = reminder_data.get('event', 'Unknown Contest')
        platform = reminder_data.get('platform', 'Unknown')
        start_time = reminder_data.get('start_time', 'TBA')
        notification_time = reminder_data.get('notification_time', '')
        
        # Format notification time for display
        notification_display = "Unknown"
        if notification_time:
            try:
                dt = datetime.strptime(notification_time, "%Y-%m-%d %H:%M:%S")
                notification_display = dt.strftime("%B %d, %I:%M %p")
            except ValueError:
                pass
        
        # Create countdown text control
        countdown_text = ft.Text(
            "Calculating...",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ORANGE_700
        )
        
        def handle_remove(e):
            """Handle removing a reminder."""
            if remove_reminder(reminder_id):
                load_reminder_list()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Reminder for {event_name} removed"),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Title row with platform
                    ft.Row([
                        ft.Text(
                            event_name,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            color=ft.colors.BLUE_700,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(
                            content=ft.Text(
                                platform,
                                color=ft.colors.WHITE,
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            bgcolor=ft.colors.BLUE_500,
                            border_radius=5,
                            padding=ft.padding.all(5),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    # Details
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Contest start: {start_time}", size=14),
                            ft.Text(f"Notification: {notification_display}", size=14),
                            # Add countdown display
                            ft.Row([
                                ft.Icon(ft.Icons.TIMER, size=16, color=ft.Colors.ORANGE_700),
                                countdown_text,
                            ]),
                        ]),
                        margin=ft.margin.symmetric(vertical=10),
                    ),
                    
                    # Remove button
                    ft.Row([
                        ft.FilledTonalButton(
                            "Remove Reminder",
                            icon=ft.icons.DELETE_OUTLINE,
                            on_click=handle_remove,
                            color=ft.colors.RED_700
                        ),
                    ], alignment=ft.MainAxisAlignment.END),
                ]),
                padding=15,
            ),
        )
        
        # Store countdown text control reference for updates
        card.data = {
            'countdown_text': countdown_text,
            'notification_time': notification_time,
            'reminder_id': reminder_id
        }
        
        return card
    
    def update_countdowns():
        """Update countdown timers for all reminder cards."""
        try:
            current_time = datetime.now()
            
            for control in reminder_list.controls:
                if hasattr(control, 'data') and control.data:
                    countdown_text = control.data.get('countdown_text')
                    notification_time_str = control.data.get('notification_time')
                    
                    if countdown_text and notification_time_str:
                        try:
                            notification_time = datetime.strptime(notification_time_str, "%Y-%m-%d %H:%M:%S")
                            time_diff = (notification_time - current_time).total_seconds()
                            
                            countdown_text.value = f"Reminder in: {format_countdown(time_diff)}"
                            
                            # Change color based on urgency
                            if time_diff <= 0:
                                countdown_text.color = ft.Colors.RED_700
                            elif time_diff <= 3600:  # Less than 1 hour
                                countdown_text.color = ft.Colors.ORANGE_700
                            else:
                                countdown_text.color = ft.Colors.GREEN_700
                                
                        except ValueError:
                            countdown_text.value = "Invalid time format"
                            countdown_text.color = ft.Colors.RED_700
        except Exception as e:
            print(f"Error updating countdowns: {e}")
    
    def countdown_worker():
        """Background thread to update countdowns every second."""
        while countdown_running:
            try:
                update_countdowns()
                page.update()
                time.sleep(1)
            except Exception as e:
                print(f"Countdown worker error: {e}")
                time.sleep(1)
    
    def load_reminder_list():
        """Load and display reminders."""
        reminders = load_reminders()
        
        reminder_list.controls.clear()
        
        if not reminders:
            no_reminders_text.visible = True
            reminder_list.visible = False
        else:
            no_reminders_text.visible = False
            reminder_list.visible = True
            
            for reminder_id, reminder_data in reminders.items():
                reminder_list.controls.append(
                    create_reminder_item(reminder_id, reminder_data)
                )
    
    # Layout - Updated to include permission controls
    content = ft.Column(
        [
            header,
            ft.Container(height=10),
            info_text,
            ft.Container(height=10),
            
            # Permission management section
            ft.Container(
                content=ft.Column([
                    ft.Text("Notification Permissions", 
                           weight=ft.FontWeight.BOLD, 
                           size=16, 
                           color=ft.Colors.BLUE_700),
                    status_text,
                    ft.Container(height=5),
                    check_permission_button,
                    ft.Container(height=5),
                    request_permission_button,
                    ft.Container(height=5),
                    test_notification_button,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                padding=15,
                margin=ft.margin.symmetric(vertical=10),
            ),
            
            ft.Container(height=15),
            no_reminders_text,
            reminder_list,
        ],
        spacing=0,
        expand=True
    )
    
    # Add content to page
    page.add(content)
    
    # Initial load
    load_reminder_list()
    
    # Ensure reminder monitor is running
    ensure_reminder_monitor_running()
    
    # Start countdown update thread
    countdown_thread = threading.Thread(target=countdown_worker, daemon=True)
    countdown_thread.start()
    
    # Check initial permission status
    initial_permission = ph.check_permission(fph.PermissionType.NOTIFICATION)
    status_text.value = f"Notification Permission: {initial_permission}"
    test_notification_button.disabled = not initial_permission
    status_text.color = ft.Colors.GREEN if initial_permission else ft.Colors.RED
    page.update()
    
    # Cleanup function (call this when leaving the page if needed)
    def cleanup():
        nonlocal countdown_running
        countdown_running = False