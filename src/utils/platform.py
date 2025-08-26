"""
Platform-specific utility functions.

This module provides cross-platform functionality for
handling system-specific operations and paths.
"""

import platform
import os
from pathlib import Path
from typing import Dict, Any


def get_platform_info() -> Dict[str, Any]:
    """
    Get information about the current platform.
    
    Returns:
        Dict containing platform information
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'is_windows': platform.system() == 'Windows',
        'is_macos': platform.system() == 'Darwin',
        'is_linux': platform.system() == 'Linux'
    }


def get_terminal_size() -> tuple[int, int]:
    """
    Get the current terminal size.
    
    Returns:
        Tuple of (columns, rows)
    """
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        # Fallback to reasonable defaults
        return 80, 24


def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def get_home_directory() -> Path:
    """
    Get the user's home directory.
    
    Returns:
        Path to user's home directory
    """
    return Path.home()


def get_temp_directory() -> Path:
    """
    Get the system's temporary directory.
    
    Returns:
        Path to system temporary directory
    """
    return Path.cwd() / "tmp" if os.environ.get("TEMP") is None else Path(os.environ["TEMP"])


def is_executable_available(command: str) -> bool:
    """
    Check if a command/executable is available in the system PATH.
    
    Args:
        command: Command name to check
        
    Returns:
        bool: True if command is available, False otherwise
    """
    from shutil import which
    return which(command) is not None


def get_environment_variable(var_name: str, default: str = None) -> str:
    """
    Get an environment variable with optional default.
    
    Args:
        var_name: Name of environment variable
        default: Default value if variable is not set
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(var_name, default)