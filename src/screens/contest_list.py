# screens/contest_list.py
import flet as ft
from services.api_client import (
    get_upcoming_contests, 
    get_available_platforms, 
    get_last_refresh_time,
    can_refresh_platform
)
from services.background_fetcher import ContestBackgroundFetcher
from components.contest_card import create_contest_card
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def contest_list_page(page: ft.Page, navigate_to):
    page.title = "Upcoming Coding Contests"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Initialize services
    background_fetcher = ContestBackgroundFetcher()
    
    # Get all available platforms
    platforms = get_available_platforms()
    platform_domains = [p["domain"] for p in platforms]

    # UI Components
    progress_ring = ft.ProgressRing(visible=False)
    loading_text = ft.Text("Loading contests...", visible=False)
    
    refresh_button = ft.IconButton(
        icon=ft.icons.REFRESH,
        tooltip="Refresh contests",
        disabled=False
    )
    
    sync_status = ft.Text(
        "Last synced: Never",
        color=ft.colors.GREY_700,
        size=12,
        visible=False
    )
    
    no_contests_text = ft.Text(
        "No upcoming contests available.",
        color=ft.Colors.RED_500,
        size=16,
        weight=ft.FontWeight.BOLD,
        visible=False
    )
    
    contest_list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=False
    )
    
    # Platform filter dropdown
    platform_dropdown = ft.Dropdown(
        label="Platform Filter",
        width=200,
        options=[
            ft.dropdown.Option(text="All Platforms", key="all"),
        ] + [
            ft.dropdown.Option(text=platform["name"], key=platform["domain"])
            for platform in platforms
        ],
        value="all"
    )

    def update_sync_status():
        """Update the last synced time display for all platforms."""
        timestamps = []
        for platform in platform_domains:
            timestamp = get_last_refresh_time(platform)
            if timestamp != "Never":
                timestamps.append(timestamp)
        
        if timestamps:
            latest_timestamp = max(timestamps)
            sync_status.value = f"Last synced: {latest_timestamp}"
            sync_status.visible = True
        else:
            sync_status.value = "Last synced: Never"
            sync_status.visible = True
        
        page.update()

    def on_background_fetch_complete():
        """Callback when background fetch completes."""
        progress_ring.visible = False
        loading_text.visible = False
        refresh_button.disabled = False
        update_sync_status()
        display_cached_contests(platform_dropdown.value)
        page.update()

    def display_cached_contests(selected_platform=None):
        """Display contests from cache for selected platform."""
        contest_list_view.controls.clear()
        
        # Determine which platforms to display
        platforms_to_display = []
        if selected_platform == "all" or not selected_platform:
            platforms_to_display = platform_domains
        else:
            platforms_to_display = [selected_platform]
        
        all_cached_contests = get_upcoming_contests(
            platforms=platforms_to_display,
            use_cache_only=True,
            limit=20  # Fetch more to allow for filtering
        )
        
        # Sort by start time
        all_cached_contests.sort(key=lambda x: x.get('start_datetime', ''))
        
        if not all_cached_contests:
            no_contests_text.visible = True
            contest_list_view.visible = False
        else:
            no_contests_text.visible = False
            contest_list_view.visible = True
            
            # Display contests
            for contest in all_cached_contests[:10]:  # Show top 10 contests
                contest_list_view.controls.append(create_contest_card(contest, page))
        
        page.update()

    def handle_platform_change(e):
        """Handle platform filter change."""
        display_cached_contests(e.control.value)

    def refresh_contests(e=None):
        """Handle manual refresh."""
        # Check if any platform can be refreshed (cache expired)
        refresh_allowed = any(can_refresh_platform(p) for p in platform_domains)
        
        if not refresh_allowed and not e:
            # Initial load - just display cached contests
            display_cached_contests(platform_dropdown.value)
            update_sync_status()
            return
        elif not refresh_allowed:
            # Manual refresh but cache is still valid
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "Cache is still valid (refresh available after 1 hour). "
                    "Using cached data."
                ),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Start the refresh
        refresh_button.disabled = True
        progress_ring.visible = True
        loading_text.visible = True
        page.update()
        
        # Start background fetch for all platforms
        background_fetcher.start_background_fetch(
            platforms=platform_domains,
            on_complete=on_background_fetch_complete,
            force_refresh=False  # Use cache rules
        )

    # Connect event handlers
    platform_dropdown.on_change = handle_platform_change
    refresh_button.on_click = lambda e: refresh_contests(e)

    # Layout
    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Upcoming Coding Contests", 
                                size=24, 
                                weight=ft.FontWeight.BOLD),
                        refresh_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                sync_status,
                ft.Row(
                    [platform_dropdown],
                    alignment=ft.MainAxisAlignment.START,
                ),
                progress_ring,
                loading_text,
                no_contests_text,
                contest_list_view
            ],
            expand=True,
            spacing=15
        )
    )

    # Initial load (this will display cached contests if available)
    refresh_contests()