# services/background_fetcher.py
import threading
import logging
from typing import List, Callable, Optional
from services.api_client import get_upcoming_contests, can_refresh_platform

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContestBackgroundFetcher:
    """
    Handles background fetching of contest data with respect to caching rules.
    """
    def __init__(self):
        self.is_fetching = False
        self.fetch_lock = threading.Lock()
    
    def start_background_fetch(
        self, 
        platforms: List[str], 
        on_complete: Optional[Callable] = None,
        force_refresh: bool = False
    ):
        """
        Start a background thread to fetch contest data.
        
        Args:
            platforms (List[str]): List of platform domains to fetch
            on_complete (Callable, optional): Callback to execute after fetch completes
            force_refresh (bool): Whether to force refresh regardless of cache validity
        """
        with self.fetch_lock:
            if self.is_fetching:
                logger.info("A fetch operation is already in progress")
                return
            self.is_fetching = True
        
        def fetch_worker():
            logger.info(f"Starting background fetch for platforms: {platforms}")
            
            try:
                # Filter platforms that actually need refreshing
                platforms_to_refresh = []
                
                if force_refresh:
                    platforms_to_refresh = platforms
                else:
                    for platform in platforms:
                        if can_refresh_platform(platform):
                            platforms_to_refresh.append(platform)
                
                if platforms_to_refresh:
                    logger.info(f"Refreshing data for: {platforms_to_refresh}")
                    get_upcoming_contests(
                        platforms=platforms_to_refresh,
                        limit=10,  # Fetch more contests per platform
                        force_refresh=True
                    )
                else:
                    logger.info("No platforms need refreshing (cache is still valid)")
                
            except Exception as e:
                logger.error(f"Error in background fetch: {str(e)}")
            finally:
                with self.fetch_lock:
                    self.is_fetching = False
                
                # Execute callback if provided
                if on_complete:
                    on_complete()
                
                logger.info("Background fetch completed")
        
        # Start the worker thread
        thread = threading.Thread(target=fetch_worker)
        thread.daemon = True
        thread.start()
    
    def is_fetch_in_progress(self) -> bool:
        """Check if a fetch operation is currently in progress."""
        with self.fetch_lock:
            return self.is_fetching