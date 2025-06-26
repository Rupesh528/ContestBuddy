# Database module initialization
# This file marks the database directory as a Python package

# Import database components for easier access
from database.mongodb_client import MongoDB
from database.session_manager import SessionManager

# Define what gets imported with 'from database import *'
__all__ = ['MongoDB', 'SessionManager']