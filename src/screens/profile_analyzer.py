# screens/profile_analyzer.py
import flet as ft
from services.profile_service import ProfileAnalyzer
import json
import os
import asyncio
import threading


def profile_analyzer_page(page: ft.Page, navigate_to):
    
    page.title = "Profile Analyzer"
    analyzer = ProfileAnalyzer()
    
    preferences_file = "user_preferences.json"
    if not os.path.exists(preferences_file):
        # If no profile is set, redirect to profile page
        navigate_to("/profile")
        return
        
    with open(preferences_file, 'r') as f:
        saved_preferences = json.load(f)

    # Container to hold all platform cards
    platforms_container = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
    error_text = ft.Text(color=ft.Colors.RED_500, visible=False, size=14)
    loading = ft.ProgressRing(width=30, height=30, visible=False)
    
    def create_section(title, elements):
        """Create a section with title and content elements"""
        return ft.Column([
            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Container(
                content=ft.Column(elements, spacing=6, tight=True),
                padding=ft.padding.only(left=8),
                margin=ft.margin.only(bottom=10)
            )
        ], tight=True)
    
    def format_label_value(label, value, color=None):
        """Create a formatted row with label and value"""
        return ft.Row([
            ft.Text(f"{label}:", size=12, color=ft.Colors.GREY_700),
            ft.Text(f"{value}", size=12, color=color or ft.Colors.BLUE_800, weight=ft.FontWeight.W_500)
        ], spacing=5)
    
    def get_rating_color(platform, rating):
        """Get color based on rating and platform"""
        if platform == "codeforces":
            try:
                rating_val = int(rating)
                if rating_val >= 2400:
                    return ft.Colors.RED
                elif rating_val >= 2100:
                    return ft.Colors.ORANGE
                elif rating_val >= 1900:
                    return ft.Colors.PURPLE
                elif rating_val >= 1600:
                    return ft.Colors.BLUE
                elif rating_val >= 1400:
                    return ft.Colors.CYAN
                else:
                    return ft.Colors.GREEN
            except:
                return ft.Colors.GREY
        elif platform == "codechef":
            if rating and rating.isdigit():
                rating_val = int(rating)
                if rating_val >= 2500:
                    return ft.Colors.RED
                elif rating_val >= 2200:
                    return ft.Colors.ORANGE
                elif rating_val >= 2000:
                    return ft.Colors.PURPLE
                elif rating_val >= 1800:
                    return ft.Colors.BLUE
                elif rating_val >= 1600:
                    return ft.Colors.CYAN
                else:
                    return ft.Colors.GREEN
        elif platform == "atcoder":
            color_map = {"red": ft.Colors.RED, "orange": ft.Colors.ORANGE, "yellow": ft.Colors.YELLOW, 
                        "blue": ft.Colors.BLUE, "cyan": ft.Colors.CYAN, "green": ft.Colors.GREEN, 
                        "brown": ft.Colors.BROWN, "gray": ft.Colors.GREY}
            return color_map.get(str(rating).lower(), ft.Colors.GREY)
        
        return ft.Colors.BLUE_800
    
    def create_stats_chip(title, value, color=None):
        """Create a compact stats chip"""
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=10, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
                ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=color or ft.Colors.BLUE_800, text_align=ft.TextAlign.CENTER),
            ], tight=True, spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=8,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            width=80,
        )
    
    def get_platform_icon(platform):
        """Get appropriate icon for each platform"""
        icons = {
            "codeforces": ft.icons.CODE,
            "leetcode": ft.icons.PSYCHOLOGY,
            "codechef": ft.icons.RESTAURANT,
            "atcoder": ft.icons.SETTINGS
        }
        return icons.get(platform, ft.icons.COMPUTER)
    
    def get_platform_color(platform):
        """Get theme color for each platform"""
        colors = {
            "codeforces": ft.Colors.BLUE_700,
            "leetcode": ft.Colors.ORANGE_700,
            "codechef": ft.Colors.BROWN_700,
            "atcoder": ft.Colors.GREEN_700
        }
        return colors.get(platform, ft.Colors.BLUE_700)
    
    def create_platform_card(platform, data):
        """Create a card for each platform"""
        if 'error' in data:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(get_platform_icon(platform), color=get_platform_color(platform), size=20),
                            ft.Text(platform.title(), size=16, weight=ft.FontWeight.BOLD, color=get_platform_color(platform)),
                        ], spacing=8),
                        ft.Text(f"Error: {data['error']}", color=ft.Colors.RED_500, size=12),
                    ], spacing=10),
                    padding=15,
                ),
                elevation=2,
            )
        
        username = data.get('handle', data.get('username', ''))
        stats_chips = []
        details = []
        
        # Platform-specific data extraction
        if platform == "codeforces":
            rating = data.get('rating', 'Unrated')
            rating_color = get_rating_color(platform, rating)
            
            stats_chips = [
                create_stats_chip("Rating", str(rating), rating_color),
                create_stats_chip("Rank", data.get('rank', 'Unranked')),
                create_stats_chip("Solved", str(data.get('accepted_submissions', 0))),
                create_stats_chip("Streak", f"{data.get('max_streak', 0)}d"),
            ]
            
            if data.get('top_languages'):
                details.append(create_section("Languages", [
                    ft.Text(lang, size=11, color=ft.Colors.BLUE_800) 
                    for lang in data['top_languages'][:2]
                ]))
                
        elif platform == "leetcode":
            total = data.get('total_solved', 0)
            
            stats_chips = [
                create_stats_chip("Total", str(total)),
                create_stats_chip("Easy", str(data.get('easy_solved', 0)), ft.Colors.GREEN),
                create_stats_chip("Medium", str(data.get('medium_solved', 0)), ft.Colors.ORANGE),
                create_stats_chip("Hard", str(data.get('hard_solved', 0)), ft.Colors.RED),
            ]
            
        elif platform == "codechef":
            rating_color = get_rating_color(platform, data.get('rating', 'Unrated'))
            
            stats_chips = [
                create_stats_chip("Rating", str(data.get('rating', 'Unrated')), rating_color),
                create_stats_chip("Stars", data.get('stars', '0')),
                create_stats_chip("Solved", str(data.get('problems_solved', 0))),
                create_stats_chip("Rank", data.get('global_rank', 'Unranked')),
            ]
            
        elif platform == "atcoder":
            rating_color = get_rating_color(platform, data.get('rating_color', 'gray'))
            
            stats_chips = [
                create_stats_chip("Rating", str(data.get('rating', 'Unrated')), rating_color),
                create_stats_chip("Class", data.get('class', 'Unranked')),
                create_stats_chip("Solved", str(data.get('problems_solved', 0))),
                create_stats_chip("Matches", str(data.get('rated_matches', 0))),
            ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header with platform name and username
                    ft.Row([
                        ft.Icon(get_platform_icon(platform), color=get_platform_color(platform), size=20),
                        ft.Column([
                            ft.Text(platform.title(), size=16, weight=ft.FontWeight.BOLD, color=get_platform_color(platform)),
                            ft.Text(f"@{username}", size=12, color=ft.Colors.GREY_700),
                        ], spacing=0, tight=True),
                    ], spacing=8),
                    
                    # Stats chips
                    ft.Container(
                        content=ft.Row(stats_chips, spacing=8, scroll=ft.ScrollMode.AUTO),
                        margin=ft.margin.only(top=10, bottom=5)
                    ),
                    
                    # Additional details
                    *details
                ], spacing=8, tight=True),
                padding=15,
            ),
            elevation=2,
        )
    
    def analyze_all_profiles():
        """Analyze profiles for all configured platforms"""
        loading.visible = True
        error_text.visible = False
        platforms_container.controls.clear()
        page.update()
        
        platform_configs = [
            ("codeforces", saved_preferences.get('codeforces_username')),
            ("leetcode", saved_preferences.get('leetcode_username')),
            ("codechef", saved_preferences.get('codechef_username')),
            ("atcoder", saved_preferences.get('atcoder_username')),
        ]
        
        # Filter only platforms with usernames configured
        configured_platforms = [(platform, username) for platform, username in platform_configs if username and username.strip()]
        
        if not configured_platforms:
            error_text.value = "No platform usernames configured. Please set them in your Profile."
            error_text.visible = True
            loading.visible = False
            page.update()
            return
        
        def fetch_profile_data(platform, username):
            """Fetch data for a single platform"""
            try:
                if platform == "codeforces":
                    return platform, analyzer.get_codeforces_profile(username)
                elif platform == "leetcode":
                    return platform, analyzer.get_leetcode_profile(username)
                elif platform == "codechef":
                    return platform, analyzer.get_codechef_profile(username)
                elif platform == "atcoder":
                    return platform, analyzer.get_atcoder_profile(username)
            except Exception as e:
                return platform, {"error": f"Failed to fetch data: {str(e)}"}
        
        # Fetch all platform data
        results = []
        for platform, username in configured_platforms:
            result = fetch_profile_data(platform, username)
            results.append(result)
        
        # Create cards for each platform
        for platform, data in results:
            card = create_platform_card(platform, data)
            platforms_container.controls.append(card)
        
        loading.visible = False
        page.update()
    
    # Create header with refresh button
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: navigate_to("/"),
                    icon_color=ft.Colors.BLUE_900,
                ),
                ft.Column([
                    ft.Text("Profile Analysis", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.BLUE_900),
                    ft.Text("All configured platforms", size=12, color=ft.Colors.GREY_700),
                ], spacing=0, tight=True, expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click=lambda _: analyze_all_profiles(),
                    icon_color=ft.Colors.BLUE_900,
                    tooltip="Refresh all profiles",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=15,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column([
            ft.Row([
                loading,
                ft.Text("Loading profiles...", size=14, color=ft.Colors.GREY_700) if loading.visible else ft.Container(),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            error_text,
            platforms_container,
        ], spacing=15, scroll=ft.ScrollMode.AUTO),
        padding=20,
        expand=True,
    )
    
    page.add(
        ft.Column([
            header,
            content,
        ], spacing=0, expand=True)
    )
    
    # Auto-load profiles on page load
    analyze_all_profiles()