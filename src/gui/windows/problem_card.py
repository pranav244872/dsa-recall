"""
Problem Card window for DSA Recall GUI.

This window shows a detailed card view of a problem with edit capabilities.
"""

import webbrowser

from src.utils.spaced_repetition import mark_problem_easy, mark_problem_hard
from src.utils.editor import edit_approach, edit_code


def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_problem_card_window(db_manager, problem):
    """
    Show the problem card window.
    
    Args:
        db_manager: Database manager instance
        problem: Problem instance to display
        
    Returns:
        bool: True if problem was updated, False otherwise
    """
    while True:
        clear_screen()
        
        print(f"Problem Card: {problem.title}")
        print("=" * 60)
        print()
        
        print(f"Title: {problem.title}")
        print(f"Link: {problem.link or '(not set)'}")
        print(f"Streak Level: {problem.streak_level}")
        print(f"Next Review: {problem.next_review or 'Not set'}")
        print(f"Last Marked: {problem.last_marked or 'Never'}")
        print()
        
        # Show approach if available
        if problem.approach.strip():
            print("Approach:")
            print("-" * 20)
            # Show first 200 characters
            approach_preview = problem.approach[:200]
            if len(problem.approach) > 200:
                approach_preview += "..."
            print(approach_preview)
            print()
        else:
            print("Approach: (not set)")
            print()
        
        # Show code if available
        if problem.code.strip():
            print("Code:")
            print("-" * 20)
            # Show first 200 characters
            code_preview = problem.code[:200]
            if len(problem.code) > 200:
                code_preview += "..."
            print(code_preview)
            print()
        else:
            print("Code: (not set)")
            print()
        
        print("Actions:")
        print("[e] Mark as Easy ✅")
        print("[h] Mark as Hard ❌")
        print("[t] Edit title")
        print("[l] Edit link")
        print("[a] Edit approach (external editor)")
        print("[c] Edit code (external editor)")
        if problem.link:
            print("[o] Open link in browser")
        print("[s] Save changes")
        print("[b] Back to previous screen")
        
        try:
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == 'e':
                mark_problem_easy(problem)
                db_manager.update_problem(problem)
                db_manager.record_daily_review()
                print(f"✅ Marked '{problem.title}' as Easy!")
                input("Press Enter to continue...")
                return True
            elif choice == 'h':
                mark_problem_hard(problem)
                db_manager.update_problem(problem)
                db_manager.record_daily_review()
                print(f"❌ Marked '{problem.title}' as Hard!")
                input("Press Enter to continue...")
                return True
            elif choice == 't':
                new_title = input(f"Enter new title (current: {problem.title}): ").strip()
                if new_title:
                    problem.title = new_title
                    print("✅ Title updated!")
                else:
                    print("❌ Title cannot be empty!")
                input("Press Enter to continue...")
            elif choice == 'l':
                new_link = input(f"Enter new link (current: {problem.link or '(not set)'}): ").strip()
                problem.link = new_link
                print("✅ Link updated!")
                input("Press Enter to continue...")
            elif choice == 'a':
                try:
                    edited_approach = edit_approach(problem.approach)
                    if edited_approach is not None:
                        problem.approach = edited_approach
                        print("✅ Approach updated!")
                    else:
                        print("⚠️  Approach editing cancelled")
                except Exception as e:
                    print(f"❌ Failed to open editor: {str(e)}")
                input("Press Enter to continue...")
            elif choice == 'c':
                try:
                    edited_code = edit_code(problem.code)
                    if edited_code is not None:
                        problem.code = edited_code
                        print("✅ Code updated!")
                    else:
                        print("⚠️  Code editing cancelled")
                except Exception as e:
                    print(f"❌ Failed to open editor: {str(e)}")
                input("Press Enter to continue...")
            elif choice == 'o' and problem.link:
                try:
                    webbrowser.open(problem.link)
                    print("✅ Opened link in browser!")
                except Exception as e:
                    print(f"❌ Failed to open link: {str(e)}")
                input("Press Enter to continue...")
            elif choice == 's':
                try:
                    db_manager.update_problem(problem)
                    print("✅ Problem saved successfully!")
                except Exception as e:
                    print(f"❌ Failed to save problem: {str(e)}")
                input("Press Enter to continue...")
            else:
                print("Invalid choice! Please try again.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            break
    
    return False