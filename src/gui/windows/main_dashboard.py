"""
Main dashboard window for DSA Recall GUI.

This window shows the main dashboard with due problems and navigation buttons.
"""

import webbrowser
from datetime import date

from src.config import MAIN_MENU_OPTIONS

def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_dashboard(db_manager):
    """
    Show the main dashboard window.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        str: Action to take based on user input
    """
    while True:
        clear_screen()
        
        # Header
        print("🧠 DSA Recall - Main Dashboard")
        print("=" * 50)
        print("Spaced Repetition for DSA Problems")
        print()
        
        # Get due problems
        due_problems = db_manager.get_due_problems()
        
        print("📅 Problems Due Today:")
        print("-" * 30)
        
        if not due_problems:
            print("🎉 No problems due for review today!")
            print("Come back tomorrow or add new problems.")
        else:
            for i, problem in enumerate(due_problems, 1):
                print(f"{i}. {problem.title} (Streak: {problem.streak_level})")
        
        print("\n" + "=" * 50)
        print("Navigation Options:")
        print("[v<ID>] View Problem (e.g., v1)")
        print("[a] ➕ Add Problem")
        print("[b] 📖 View All Problems") 
        print("[s] 🔥 View Streak Tracker")
        print("[q] 🚪 Exit")
        print()
        
        try:
            choice = input("Enter your choice: ").strip().lower()
            
            if choice == 'q':
                return 'exit'
            elif choice == 'a':
                return 'add_problem'
            elif choice == 'b':
                return 'all_problems'
            elif choice == 's':
                return 'streak_tracker'
            elif choice.startswith('v') and len(choice) > 1:
                # View problem
                try:
                    problem_index = int(choice[1:]) - 1
                    if 0 <= problem_index < len(due_problems):
                        return f'view_problem:{due_problems[problem_index].id}'
                    else:
                        print("Invalid problem number!")
                        input("Press Enter to continue...")
                except (ValueError, IndexError):
                    print("Invalid input!")
                    input("Press Enter to continue...")
            else:
                print("Invalid choice! Please try again.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            return 'exit'
