# components/__init__.py
"""
Pic2Pick UI Components Package

This package contains reusable UI components for the Pic2Pick application.
"""

__version__ = "1.0.0"
__author__ = "Your Shivam Kumar"

# Import all components
from .navbar import render_navbar
from .footer import render_footer

# Define what gets imported with "from components import *"
__all__ = [
    'render_navbar',
    'render_footer'
]