# services/reminder_service.py
import json
import os
import threading
import time
from datetime import datetime, timedelta
import logging
import flet as ft
import flet_permission_handler as fph
from jnius import autoclass

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File to store reminders
REMINDERS_FILE = "contest_reminders.json"

# Get the app directory path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reminders_path = os.path.join(base_dir, REMINDERS_FILE)

# Default reminder time (minutes before contest)
DEFAULT_REMINDER_TIME = 30

def load_reminders():
    """Load reminders from storage file."""
    if os.path.exists(reminders_path):
        try:
            with open(reminders_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading reminders: {str(e)}")
    return {}

def save_reminders(reminders):
    """Save reminders to storage file."""
    try:
        with open(reminders_path, 'w') as f:
            json.dump(reminders, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Error saving reminders: {str(e)}")
        return False

def parse_datetime_string(datetime_str):
    """Parse datetime string to datetime object."""
    try:
        # Extract the date and time part (excluding IST)
        dt_part = datetime_str.split(" IST")[0]
        # Parse datetime with specific format
        return datetime.strptime(dt_part, "%Y-%m-%d %I:%M %p")
    except ValueError as e:
        logger.error(f"Error parsing datetime: {str(e)}")
        return None

def add_reminder(contest):
    """
    Add a reminder for a contest.
    
    Args:
        contest (dict): Contest information
        
    Returns:
        bool: Success status
    """
    contest_id = contest.get('id')
    if not contest_id:
        logger.error("Cannot add reminder: Contest ID missing")
        return False
    
    start_datetime_str = contest.get('start_datetime')
    if not start_datetime_str:
        logger.error("Cannot add reminder: Start time missing")
        return False
    
    # Parse start datetime
    start_datetime = parse_datetime_string(start_datetime_str)
    if not start_datetime:
        logger.error(f"Cannot parse start time: {start_datetime_str}")
        return False
    
    # Calculate notification time (30 minutes before start)
    notification_time = start_datetime - timedelta(minutes=DEFAULT_REMINDER_TIME)
    
    # Create reminder data
    reminder = {
        "id": contest_id,
        "event": contest.get('event', 'Contest'),
        "platform": contest.get('platform_display_name', 'Unknown'),
        "start_time": start_datetime_str,
        "notification_time": notification_time.strftime("%Y-%m-%d %H:%M:%S"),
        "url": contest.get('href', '#'),
        "notified": False  # Track if notification was sent
    }
    
    # Load existing reminders
    reminders = load_reminders()
    
    # Add new reminder
    reminders[str(contest_id)] = reminder
    
    # Save updated reminders
    if save_reminders(reminders):
        # Start the reminder monitor if not already running
        ensure_reminder_monitor_running()
        logger.info(f"Reminder added for contest: {contest.get('event')} at {notification_time}")
        return True
    
    return False

def remove_reminder(contest_id):
    """
    Remove a reminder for a contest.
    
    Args:
        contest_id: ID of the contest
        
    Returns:
        bool: Success status
    """
    reminders = load_reminders()
    
    contest_id_str = str(contest_id)
    if contest_id_str in reminders:
        del reminders[contest_id_str]
        return save_reminders(reminders)
    
    return False

def is_reminder_set(contest_id):
    """
    Check if a reminder is set for a contest.
    
    Args:
        contest_id: ID of the contest
        
    Returns:
        bool: True if reminder is set
    """
    reminders = load_reminders()
    return str(contest_id) in reminders

def send_notification(title, text):
    """Send a notification using Android's notification system."""
    try:
        # Get the main activity from the environment
        activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
        assert activity_host_class, "Activity host class not found in environment"
        activity_host = autoclass(activity_host_class)
        activity = activity_host.mActivity

        # Access the Android notification manager
        Context = autoclass('android.content.Context')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        Notification = autoclass('android.app.Notification')
        NotificationBuilder = autoclass('android.app.Notification$Builder')

        # Start the notification service
        notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)

        # Create a notification channel (for Android 8.0 and above)
        channel_id = "contest_reminders_channel"
        channel_name = "Contest Reminders"
        importance = NotificationManager.IMPORTANCE_DEFAULT

        # Create the notification channel (Android 8.0+)
        channel = NotificationChannel(channel_id, channel_name, importance)
        notification_service.createNotificationChannel(channel)

        # Build the notification
        builder = NotificationBuilder(activity, channel_id)
        builder.setContentTitle(title)
        builder.setContentText(text)
        builder.setSmallIcon(activity.getApplicationInfo().icon)
        builder.setAutoCancel(True)

        # Display the notification
        notification_id = hash(title + text) % 10000  # Generate somewhat unique ID
        notification = builder.build()
        notification_service.notify(notification_id, notification)
        
        logger.info(f"Notification sent: {title}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return False

# Singleton monitor instance
_monitor_thread = None
_monitor_running = False
_monitor_lock = threading.Lock()

def reminder_monitor_worker():
    """Worker thread to monitor and trigger reminders."""
    global _monitor_running
    
    logger.info("Reminder monitor started")
    
    while _monitor_running:
        try:
            current_time = datetime.now()
            reminders = load_reminders()
            reminders_to_remove = []
            reminders_updated = False
            
            logger.debug(f"Checking {len(reminders)} reminders at {current_time}")
            
            for contest_id, reminder in reminders.items():
                notification_time_str = reminder.get('notification_time')
                if not notification_time_str:
                    continue
                
                # Skip if already notified
                if reminder.get('notified', False):
                    continue
                
                try:
                    notification_time = datetime.strptime(notification_time_str, "%Y-%m-%d %H:%M:%S")
                    
                    # Check if countdown has reached zero (notification time has passed)
                    time_diff = (notification_time - current_time).total_seconds()
                    
                    if time_diff <= 0:  # Countdown reached zero or passed
                        # Send notification
                        event_name = reminder.get('event', 'Contest')
                        platform = reminder.get('platform', 'Unknown')
                        start_time = reminder.get('start_time', 'Unknown time')
                        
                        title = f"🏆 {platform} Contest Reminder"
                        message = f"{event_name} starts at {start_time}"
                        
                        logger.info(f"Countdown reached zero! Sending notification for contest: {event_name}")
                        
                        if send_notification(title, message):
                            # Mark as notified to prevent duplicate notifications
                            reminder['notified'] = True
                            reminders[contest_id] = reminder
                            reminders_updated = True
                            logger.info(f"Notification sent and marked for contest: {event_name}")
                        else:
                            logger.error(f"Failed to send notification for contest: {event_name}")
                    
                    # Clean up old reminders (contests that started more than 2 hours ago)
                    elif time_diff < -7200:  # More than 2 hours past notification time
                        logger.info(f"Removing old reminder for contest: {reminder.get('event')}")
                        reminders_to_remove.append(contest_id)
                        
                except ValueError as e:
                    logger.error(f"Error parsing notification time for contest {contest_id}: {str(e)}")
                    reminders_to_remove.append(contest_id)
            
            # Save updated reminders if any were marked as notified
            if reminders_updated:
                save_reminders(reminders)
                logger.info("Updated reminder statuses saved")
            
            # Remove old reminders
            if reminders_to_remove:
                updated_reminders = reminders.copy()
                for contest_id in reminders_to_remove:
                    updated_reminders.pop(contest_id, None)
                save_reminders(updated_reminders)
                logger.info(f"Removed {len(reminders_to_remove)} old reminders")
                
        except Exception as e:
            logger.error(f"Error in reminder monitor: {str(e)}")
        
        # Sleep for 15 seconds before checking again (more frequent checks for accuracy)
        time.sleep(15)
    
    logger.info("Reminder monitor stopped")

def ensure_reminder_monitor_running():
    """Ensure the reminder monitor thread is running."""
    global _monitor_thread, _monitor_running
    
    with _monitor_lock:
        if _monitor_thread is None or not _monitor_thread.is_alive():
            _monitor_running = True
            _monitor_thread = threading.Thread(target=reminder_monitor_worker)
            _monitor_thread.daemon = True
            _monitor_thread.start()
            logger.info("Reminder monitor thread started")

def request_notification_permission(page):
    """
    Request notification permission if not already granted.
    
    Args:
        page (ft.Page): Current page object
        
    Returns:
        bool: Whether permission is granted
    """
    try:
        # Add permission handler to page
        ph = fph.PermissionHandler()
        page.overlay.append(ph)
        page.update()
        
        # Check current permission status
        has_permission = ph.check_permission(fph.PermissionType.NOTIFICATION)
        
        if not has_permission:
            # Request notification permission
            has_permission = ph.request_permission(fph.PermissionType.NOTIFICATION)
            # Also request notification policy access (for Android)
            ph.request_permission(fph.PermissionType.ACCESS_NOTIFICATION_POLICY)
        
        return has_permission
    except Exception as e:
        logger.error(f"Error requesting notification permission: {str(e)}")
        return False