"""
Main dashboard window for DSA Recall GUI.

This window shows the main dashboard with due problems and navigation buttons.
"""

import webbrowser
from datetime import date

from src.config import MAIN_MENU_OPTIONS
from src.utils.spaced_repetition import mark_problem_easy, mark_problem_hard


def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def create_problem_card_display(problem):
    """
    Create text display for a single problem card.
    
    Args:
        problem: Problem instance
        
    Returns:
        str: Formatted problem card text
    """
    card_lines = []
    card_lines.append("┌" + "─" * 70 + "┐")
    card_lines.append(f"│ 📌 {problem.title:<66} │")
    
    if problem.link:
        link_text = f"🔗 {problem.link}"
        if len(link_text) > 66:
            link_text = link_text[:63] + "..."
        card_lines.append(f"│ {link_text:<66} │")
    
    card_lines.append("│" + " " * 70 + "│")
    
    # Show approach preview if available
    if problem.approach.strip():
        approach_preview = problem.approach[:60] + "..." if len(problem.approach) > 60 else problem.approach
        card_lines.append(f"│ Approach: {approach_preview:<57} │")
    
    # Show code preview if available
    if problem.code.strip():
        code_preview = problem.code[:60] + "..." if len(problem.code) > 60 else problem.code
        card_lines.append(f"│ Code: {code_preview:<61} │")
    
    card_lines.append("│" + " " * 70 + "│")
    card_lines.append(f"│ Streak: {problem.streak_level:<3} | Next Review: {str(problem.next_review or 'Not set'):<20} │")
    card_lines.append("└" + "─" * 70 + "┘")
    
    return "\n".join(card_lines)


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
                print(f"\n{i}. {create_problem_card_display(problem)}")
                print(f"   Actions: [e{i}] Easy ✅  [h{i}] Hard ❌  [v{i}] View/Edit")
        
        print("\n" + "=" * 50)
        print("Navigation Options:")
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
            elif choice.startswith('e') and len(choice) > 1:
                # Easy marking
                try:
                    problem_index = int(choice[1:]) - 1
                    if 0 <= problem_index < len(due_problems):
                        return f'mark_easy:{due_problems[problem_index].id}'
                    else:
                        print("Invalid problem number!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input!")
                    input("Press Enter to continue...")
            elif choice.startswith('h') and len(choice) > 1:
                # Hard marking
                try:
                    problem_index = int(choice[1:]) - 1
                    if 0 <= problem_index < len(due_problems):
                        return f'mark_hard:{due_problems[problem_index].id}'
                    else:
                        print("Invalid problem number!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input!")
                    input("Press Enter to continue...")
            elif choice.startswith('v') and len(choice) > 1:
                # View/Edit problem
                try:
                    problem_index = int(choice[1:]) - 1
                    if 0 <= problem_index < len(due_problems):
                        return f'view_problem:{due_problems[problem_index].id}'
                    else:
                        print("Invalid problem number!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input!")
                    input("Press Enter to continue...")
            else:
                print("Invalid choice! Please try again.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            return 'exit'