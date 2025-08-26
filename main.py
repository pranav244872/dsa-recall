#!/usr/bin/env python3
"""
DSA Recall - GUI-based Spaced Repetition for DSA Problems

Entry point for the DSA Recall application.
"""

import sys
import os

# Add src to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.app import run_app

if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)