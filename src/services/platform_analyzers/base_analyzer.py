
from abc import ABC, abstractmethod

class BaseProfileAnalyzer(ABC):
    """Base class for all platform-specific profile analyzers"""
    
    def __init__(self):
        self.timeout = 10
    
    @abstractmethod
    def get_profile(self, username):
        """Get profile details for the given username"""
        pass
    
    def format_error(self, error_msg):
        """Format error message consistently"""
        return {'error': str(error_msg)}