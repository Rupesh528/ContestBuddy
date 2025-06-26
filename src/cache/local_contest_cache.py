# cache/local_contest_cache.py
import os
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalContestCache:
    """
    Improved local caching mechanism for contest data with time-based expiration.
    """
    def __init__(self, cache_dir="cache", cache_duration_hours=1):
        """
        Initialize the cache with specified directory and expiration time.
        
        Args:
            cache_dir (str): Directory to store cache files
            cache_duration_hours (int): Cache validity period in hours
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # Ensure cache directory exists
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                cache_dir), exist_ok=True)
        
        # In-memory cache for faster repeated access
        self.memory_cache = {}
    
    def _get_cache_path(self, platform):
        """Get the file path for a platform's cache file."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.cache_dir, f"{platform}_contests.json")
    
    def _is_cache_valid(self, metadata):
        """Check if cache is still valid based on its timestamp."""
        if not metadata or "timestamp" not in metadata:
            return False
            
        cache_time = datetime.fromisoformat(metadata["timestamp"])
        current_time = datetime.now()
        
        return (current_time - cache_time) < self.cache_duration
        
    def get_cached_contests(self, platform):
        """
        Get cached contests for a platform if cache is valid.
        
        Args:
            platform (str): Platform identifier
            
        Returns:
            list: Cached contests or None if cache is invalid/missing
        """
        # Check memory cache first for faster access
        if platform in self.memory_cache:
            cache_data = self.memory_cache[platform]
            if self._is_cache_valid(cache_data["metadata"]):
                logger.info(f"Retrieved {platform} contests from memory cache")
                return cache_data["contests"]
        
        # Check file cache
        cache_path = self._get_cache_path(platform)
        
        try:
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            if self._is_cache_valid(cache_data["metadata"]):
                # Update memory cache
                self.memory_cache[platform] = cache_data
                logger.info(f"Retrieved {platform} contests from file cache")
                return cache_data["contests"]
            else:
                logger.info(f"Cache for {platform} has expired")
                return None
                
        except Exception as e:
            logger.error(f"Error reading cache for {platform}: {str(e)}")
            return None
    
    def cache_contests(self, platform, contests):
        """
        Cache contests for a platform.
        
        Args:
            platform (str): Platform identifier
            contests (list): List of contest data to cache
        """
        cache_path = self._get_cache_path(platform)
        
        try:
            # Create cache data structure with metadata
            cache_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "count": len(contests)
                },
                "contests": contests
            }
            
            # Update both memory and file cache
            self.memory_cache[platform] = cache_data
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.info(f"Cached {len(contests)} contests for {platform}")
            
        except Exception as e:
            logger.error(f"Error caching contests for {platform}: {str(e)}")
    
    def is_refresh_needed(self, platform):
        """
        Check if the cache for a platform needs to be refreshed.
        
        Args:
            platform (str): Platform identifier
            
        Returns:
            bool: True if refresh is needed, False otherwise
        """
        # Check memory cache first
        if platform in self.memory_cache:
            if self._is_cache_valid(self.memory_cache[platform]["metadata"]):
                return False
        
        # Check file cache
        cache_path = self._get_cache_path(platform)
        
        try:
            if not os.path.exists(cache_path):
                return True
                
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            return not self._is_cache_valid(cache_data["metadata"])
                
        except Exception:
            # If any error occurs, we should refresh
            return True
    
    def get_last_refresh_time(self, platform):
        """
        Get the timestamp of the last refresh for a platform.
        
        Args:
            platform (str): Platform identifier
            
        Returns:
            str: Formatted timestamp or None if not available
        """
        # Check memory cache first
        if platform in self.memory_cache:
            timestamp = self.memory_cache[platform]["metadata"].get("timestamp")
            if timestamp:
                return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Check file cache
        cache_path = self._get_cache_path(platform)
        
        try:
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            timestamp = cache_data["metadata"].get("timestamp")
            if timestamp:
                return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception:
            pass
            
        return None
        
    def clear_cache(self, platform=None):
        """
        Clear cache for a specific platform or all platforms.
        
        Args:
            platform (str, optional): Platform to clear cache for, or None for all
        """
        if platform:
            # Clear specific platform
            if platform in self.memory_cache:
                del self.memory_cache[platform]
                
            cache_path = self._get_cache_path(platform)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"Cleared cache for {platform}")
        else:
            # Clear all platforms
            self.memory_cache = {}
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(base_dir, self.cache_dir)
            
            if os.path.exists(cache_dir):
                for filename in os.listdir(cache_dir):
                    if filename.endswith("_contests.json"):
                        os.remove(os.path.join(cache_dir, filename))
                        
            logger.info("Cleared all platform caches")