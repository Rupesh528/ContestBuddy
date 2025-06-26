# Components module initialization
# This file marks the components directory as a Python package

# Import components for easier access
from components.logout_component import logout_button

# Define what gets imported with 'from components import *'
__all__ = ['logout_button']