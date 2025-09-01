"""
Main GUI application for DSA Recall.

This module contains the main GUI application window and navigation logic.
Note: Due to environment constraints, this implements a simplified GUI simulation.
"""

import sys
import webbrowser
from datetime import date

from src.database.db_manager import DatabaseManager
from src.utils.spaced_repetition import auto_mark_overdue_problems, mark_problem_easy, mark_problem_hard
from src.config import APP_TITLE

from .windows.main_dashboard import show_main_dashboard
from .windows.add_problem import show_add_problem_window
from .windows.all_problems import show_all_problems_window
from .windows.streak_tracker import show_streak_tracker_window
from .windows.problem_card import show_problem_card_window


class DSARecallGUI:
    """
    Main GUI application class for DSA Recall.
    
    Manages the main window, navigation, and application state.
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        print(f"🧠 {APP_TITLE} - GUI Version")
        print("=" * 50)
        
        # Initialize database
        self.db = DatabaseManager()
        self._auto_mark_overdue_problems()
        
        print("Application initialized successfully!")
        print("Note: This is a simplified GUI implementation for demonstration.")
        print()
    
    def _auto_mark_overdue_problems(self):
        """Auto-mark overdue problems as hard on startup."""
        overdue_problems = self.db.get_overdue_problems()
        if overdue_problems:
            count = auto_mark_overdue_problems(overdue_problems)
            # Update problems in database
            for problem in overdue_problems:
                self.db.update_problem(problem)
            
            if count > 0:
                print(f"⚠️  Auto-marked {count} overdue problem(s) as hard")
                print()
    
    def run(self):
        """Run the GUI application."""
        while True:
            try:
                # Show main dashboard
                action = show_main_dashboard(self.db)
                
                if action == 'exit':
                    break
                elif action == 'add_problem':
                    show_add_problem_window(self.db)
                elif action == 'all_problems':
                    show_all_problems_window(self.db)
                elif action == 'streak_tracker':
                    show_streak_tracker_window(self.db)
                elif action.startswith('view_problem:'):
                    # Extract problem ID from action
                    problem_id = int(action.split(':')[1])
                    problem = self.db.get_problem(problem_id)
                    if problem:
                        show_problem_card_window(self.db, problem)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")


def run_app():
    """Run the DSA Recall GUI application."""
    app = DSARecallGUI()
    app.run()
