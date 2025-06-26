# components/contest_card.py
import flet as ft
from datetime import datetime, timedelta
import json
import os
from services.reminder_service import add_reminder, is_reminder_set

def create_contest_card(contest, page):
    """
    Create a card displaying contest information with a reminder button.
    
    Args:
        contest (dict): Contest information dictionary
        page (ft.Page): Current page object for updates
        
    Returns:
        ft.Card: Contest card component
    """
    contest_id = contest.get('id', '')
    event_name = contest.get('event', 'Unknown Contest')
    platform = contest.get('platform_display_name', 'Unknown Platform')
    start_time = contest.get('start_datetime', 'TBA')
    duration_seconds = contest.get('duration', 0)
    
    # Calculate duration in hours
    duration_hours = round(duration_seconds / 3600, 1) if duration_seconds else 0
    duration_text = f"{duration_hours} hours" if duration_hours else "Unknown duration"
    
    # Contest URL
    url = contest.get('href', '#')
    
    # Check if reminder already set for this contest
    reminder_set = is_reminder_set(contest_id)
    
    # Create reminder button with appropriate state
    reminder_button = ft.ElevatedButton(
        text="✅ Reminder Set" if reminder_set else "⏰ Set Reminder",
        bgcolor=ft.colors.GREEN_700 if reminder_set else ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        data=contest,  # Store contest data for callback
        disabled=reminder_set,  # Disable if reminder already set
    )
    
    def handle_set_reminder(e):
        """Handle click on set reminder button."""
        contest_data = e.control.data
        
        # Add reminder
        success = add_reminder(contest_data)
        
        if success:
            # Update button appearance
            e.control.text = "✅ Reminder Set"
            e.control.bgcolor = ft.colors.GREEN_700
            e.control.disabled = True
            
            # Show success message
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Reminder set for {event_name}"),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
    
    reminder_button.on_click = handle_set_reminder
    
    # Card layout
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
                
                # Details row
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Start: {start_time}", size=14),
                        ft.Text(f"Duration: {duration_text}", size=14),
                    ]),
                    margin=ft.margin.symmetric(vertical=10),
                ),
                
                # Action buttons row
                ft.Row([
                    ft.TextButton(
                        content=ft.Text(
                            "Visit Website",
                            color=ft.colors.BLUE_700,
                        ),
                        url=url,
                        tooltip="Open contest page",
                    ),
                    reminder_button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            padding=15,
        ),
    )
    
    return card