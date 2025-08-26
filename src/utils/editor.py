"""
External editor integration utilities.

This module provides functionality for launching external editors
to edit long text content like problem approaches and code.
"""

import os
import tempfile
import subprocess
import platform
from pathlib import Path
from typing import Optional


def get_default_editor() -> str:
    """
    Get the default editor for the current platform.
    
    Returns:
        str: Default editor command
    """
    # Check environment variable first
    editor = os.environ.get('EDITOR')
    if editor:
        return editor
    
    # Platform-specific defaults
    system = platform.system()
    if system == "Windows":
        return "notepad"
    else:
        # Unix-like systems (Linux, macOS)
        return "nano"


def edit_text(initial_content: str = "", file_extension: str = ".txt") -> Optional[str]:
    """
    Open external editor to edit text content.
    
    Args:
        initial_content: Initial text to populate in the editor
        file_extension: File extension for temporary file (affects syntax highlighting)
        
    Returns:
        str: Edited content if successful, None if editing was cancelled or failed
    """
    editor = get_default_editor()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode='w+',
        suffix=file_extension,
        delete=False,
        encoding='utf-8'
    ) as temp_file:
        temp_file.write(initial_content)
        temp_path = temp_file.name
    
    try:
        # Launch editor
        if platform.system() == "Windows":
            # On Windows, use shell=True for notepad and similar editors
            result = subprocess.run([editor, temp_path], shell=True, check=True)
        else:
            # On Unix-like systems
            result = subprocess.run([editor, temp_path], check=True)
        
        # Read edited content
        with open(temp_path, 'r', encoding='utf-8') as temp_file:
            edited_content = temp_file.read()
        
        return edited_content
        
    except subprocess.CalledProcessError:
        # Editor was cancelled or failed
        return None
    except FileNotFoundError:
        # Editor command not found
        raise RuntimeError(f"Editor '{editor}' not found. Please set the EDITOR environment variable.")
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except OSError:
            pass  # File might already be deleted


def edit_approach(initial_content: str = "") -> Optional[str]:
    """
    Edit problem approach using external editor.
    
    Args:
        initial_content: Initial approach text
        
    Returns:
        str: Edited approach text, None if cancelled
    """
    return edit_text(initial_content, ".md")


def edit_code(initial_content: str = "", language: str = "python") -> Optional[str]:
    """
    Edit code using external editor with appropriate file extension.
    
    Args:
        initial_content: Initial code content
        language: Programming language for syntax highlighting
        
    Returns:
        str: Edited code, None if cancelled
    """
    # Map common languages to file extensions
    extensions = {
        "python": ".py",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c",
        "javascript": ".js",
        "typescript": ".ts",
        "go": ".go",
        "rust": ".rs",
        "ruby": ".rb",
        "php": ".php",
        "swift": ".swift",
        "kotlin": ".kt",
        "scala": ".scala"
    }
    
    extension = extensions.get(language.lower(), ".txt")
    return edit_text(initial_content, extension)