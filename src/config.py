"""
DSA Recall - Configuration and constants
"""

import os
import platform
from pathlib import Path

# Application metadata
APP_NAME = "dsarecall"
APP_TITLE = "DSA Recall"
VERSION = "1.0.0"

# Database configuration
DB_NAME = "dsarecall.db"

def get_data_dir() -> Path:
    """
    Get the platform-specific data directory for storing the database.
    
    Returns:
        Path: Platform-specific data directory
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: %APPDATA%/dsarecall/
        base_dir = os.environ.get("APPDATA", str(Path.home()))
        return Path(base_dir) / APP_NAME
    else:
        # Linux/macOS: ~/.config/dsarecall/
        base_dir = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(base_dir) / APP_NAME

def get_db_path() -> Path:
    """
    Get the full path to the database file.
    
    Returns:
        Path: Full path to database file
    """
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / DB_NAME

# Spaced repetition constants
INITIAL_STREAK_LEVEL = 1
INITIAL_INTERVAL_DAYS = 1
STREAK_MULTIPLIER = 2

# UI Constants
MAIN_MENU_OPTIONS = [
    "➕ Add Problem",
    "📅 Review Due Problems", 
    "📖 View All Problems",
    "🔥 View Streak Tracker",
    "🚪 Exit"
]

# Keyboard shortcuts
SHORTCUTS = {
    'toggle_approach': 'a',
    'toggle_code': 'c',
    'mark_easy': 'e',
    'mark_hard': 'h',
    'edit_problem': 'E',
    'delete_problem': 'D',
    'edit_title': 't',
    'edit_link': 'l',
    'save_changes': 's',
    'go_back': 'escape'
}