# services/api_client.py
import requests
from datetime import datetime, timezone, timedelta
import time
import logging
import os
import json
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = "Rupesh_79:17669a44745b2ef05d5093ec6290f26f3408b0a2"
BASE_URL = "https://clist.by/api/v2/contest/"

# Limited set of platforms as requested
PLATFORMS = {
    "codeforces.com": "Codeforces",
    "codechef.com": "CodeChef",
    "leetcode.com": "LeetCode", 
    "hackerrank.com": "HackerRank",
    "atcoder.jp": "AtCoder",
    "topcoder.com": "TopCoder"
}

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
        
        # Get the app directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_path = os.path.join(base_dir, cache_dir)
        
        # Ensure cache directory exists
        os.makedirs(self.cache_path, exist_ok=True)
        
        # In-memory cache for faster repeated access
        self.memory_cache = {}
    
    def _get_cache_path(self, platform):
        """Get the file path for a platform's cache file."""
        return os.path.join(self.cache_path, f"{platform}_contests.json")
    
    def _is_cache_valid(self, metadata):
        """Check if cache is still valid based on its timestamp."""
        if not metadata or "timestamp" not in metadata:
            return False
            
        try:
            cache_time = datetime.fromisoformat(metadata["timestamp"])
            current_time = datetime.now()
            
            return (current_time - cache_time) < self.cache_duration
        except (ValueError, TypeError):
            return False
        
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

# Create the improved cache with 1-hour cache duration
contest_cache = LocalContestCache(cache_duration_hours=48)

class APIRateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.window = 60  # 1 minute window

    def wait_if_needed(self):
        current_time = time.time()
        # Remove requests older than our window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.window]
        
        if len(self.requests) >= self.requests_per_minute:
            # Wait until oldest request is outside our window
            sleep_time = self.window - (current_time - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.requests = self.requests[1:]
        
        self.requests.append(current_time)

def parse_datetime(date_string: str) -> Optional[str]:
    """Parse datetime with timezone and convert to IST with AM/PM format."""
    if not date_string:
        return None
    
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(date_string, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            ist = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
            return ist.strftime("%Y-%m-%d %I:%M %p IST")
        except ValueError:
            continue
    
    logger.warning(f"Unable to parse date: {date_string}")
    return None

def get_platform_display_name(resource: str) -> str:
    """Get user-friendly platform name."""
    return PLATFORMS.get(resource, resource)

rate_limiter = APIRateLimiter()

def get_upcoming_contests(
    limit: int = 5, 
    offset: int = 0, 
    platforms: List[str] = None,
    use_cache_only: bool = False,
    force_refresh: bool = False
) -> List[Dict]:
    """
    Fetch upcoming contests from specified platforms.
    
    Args:
        limit (int): Maximum number of contests per platform
        offset (int): Offset for pagination
        platforms (List[str]): List of platform domains to fetch contests from
        use_cache_only (bool): Whether to use only cached data
        force_refresh (bool): Whether to force refresh from API
        
    Returns:
        List[Dict]: List of upcoming contests sorted by start time
    """
    all_contests = []
    resources_to_fetch = platforms if platforms else list(PLATFORMS.keys())
    
    # Filter to ensure we only fetch from supported platforms
    resources_to_fetch = [p for p in resources_to_fetch if p in PLATFORMS]
    
    for resource in resources_to_fetch:
        try:
            # Check if we need to refresh the cache
            refresh_needed = force_refresh or contest_cache.is_refresh_needed(resource)
            
            # Get cached contests if available
            cached_contests = contest_cache.get_cached_contests(resource)
            
            if cached_contests and not refresh_needed:
                all_contests.extend(cached_contests)
                logger.info(f"Using cached data for {resource}")
                continue
            
            if use_cache_only:
                if cached_contests:
                    all_contests.extend(cached_contests)
                logger.info(f"Skipping API call for {resource} (cache-only mode)")
                continue
            
            # Apply rate limiting before API call
            rate_limiter.wait_if_needed()
            
            logger.info(f"Fetching fresh data for {resource}")
            
            params = {
                "limit": limit,
                "offset": offset,
                "upcoming": "true",
                "resource": resource
            }
            
            # Add exponential backoff for retries
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        BASE_URL, 
                        headers={"Authorization": f"ApiKey {API_KEY}"}, 
                        params=params,
                        timeout=10  # Add timeout
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Retry {attempt+1}/{max_retries} for {resource} after error: {str(e)}")
                        time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise
            
            contests = response.json().get("objects", [])
            processed_contests = []
            
            for contest in contests:
                contest['start_datetime'] = parse_datetime(contest.get('start', 'N/A'))
                contest['end_datetime'] = parse_datetime(contest.get('end', 'N/A'))
                contest['platform_display_name'] = get_platform_display_name(resource)
                processed_contests.append(contest)
            
            # Cache the processed contests
            contest_cache.cache_contests(resource, processed_contests)
            all_contests.extend(processed_contests)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching contest details from {resource}: {str(e)}")
            # If API call fails, use cached data if available
            if cached_contests:
                all_contests.extend(cached_contests)
            continue
    
    # Sort contests by start time and filter out those without start time
    return sorted(
        [contest for contest in all_contests if contest.get('start_datetime')], 
        key=lambda x: x['start_datetime']
    )

def get_available_platforms() -> List[Dict[str, str]]:
    """Get list of available platforms with their display names."""
    return [
        {"domain": domain, "name": display_name} 
        for domain, display_name in PLATFORMS.items()
    ]

def get_last_refresh_time(platform: str) -> str:
    """
    Get the timestamp of the last refresh for a platform.
    
    Args:
        platform (str): Platform domain
        
    Returns:
        str: Formatted timestamp or "Never" if not available
    """
    timestamp = contest_cache.get_last_refresh_time(platform)
    return timestamp if timestamp else "Never"

def can_refresh_platform(platform: str) -> bool:
    """
    Check if a platform can be refreshed (cache is expired).
    
    Args:
        platform (str): Platform domain
        
    Returns:
        bool: True if refresh is allowed, False otherwise
    """
    return contest_cache.is_refresh_needed(platform)