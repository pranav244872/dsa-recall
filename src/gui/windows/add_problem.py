"""
Add Problem window for DSA Recall GUI.

This window allows users to add new DSA problems with external editor integration.
"""

from src.database.models import Problem
from src.utils.spaced_repetition import initialize_new_problem
from src.utils.editor import edit_approach, edit_code


def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_add_problem_window(db_manager):
    """
    Show the add problem window.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        bool: True if problem was added, False if cancelled
    """
    clear_screen()
    
    print("➕ Add New Problem")
    print("=" * 30)
    print()
    
    # Initialize problem
    problem = Problem()
    
    # Get title
    while True:
        title = input("Title (required): ").strip()
        if title:
            problem.title = title
            break
        else:
            print("❌ Title is required!")
    
    # Get link
    link = input("Link (optional): ").strip()
    problem.link = link
    
    # Approach section
    print("\nApproach:")
    print("[1] Edit approach in external editor")
    print("[2] Skip approach")
    
    approach_choice = input("Choose option (1-2): ").strip()
    if approach_choice == '1':
        try:
            edited_approach = edit_approach(problem.approach)
            if edited_approach is not None:
                problem.approach = edited_approach
                print("✅ Approach added successfully!")
            else:
                print("⚠️  Approach editing cancelled")
        except Exception as e:
            print(f"❌ Failed to open editor: {str(e)}")
    
    # Code section
    print("\nCode:")
    print("[1] Edit code in external editor")
    print("[2] Skip code")
    
    code_choice = input("Choose option (1-2): ").strip()
    if code_choice == '1':
        try:
            edited_code = edit_code(problem.code)
            if edited_code is not None:
                problem.code = edited_code
                print("✅ Code added successfully!")
            else:
                print("⚠️  Code editing cancelled")
        except Exception as e:
            print(f"❌ Failed to open editor: {str(e)}")
    
    # Show summary
    print("\n" + "=" * 50)
    print("Problem Summary:")
    print(f"Title: {problem.title}")
    print(f"Link: {problem.link or '(not set)'}")
    print(f"Approach: {'✅ Set' if problem.approach.strip() else '❌ Not set'}")
    print(f"Code: {'✅ Set' if problem.code.strip() else '❌ Not set'}")
    print()
    
    # Confirm save
    while True:
        confirm = input("Save this problem? [y/N]: ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                # Initialize spaced repetition metadata
                initialize_new_problem(problem)
                
                # Save to database
                problem_id = db_manager.add_problem(problem)
                print(f"✅ Problem '{problem.title}' added successfully! (ID: {problem_id})")
                input("Press Enter to continue...")
                return True
            except Exception as e:
                print(f"❌ Failed to save problem: {str(e)}")
                input("Press Enter to continue...")
                return False
        elif confirm in ['n', 'no', '']:
            print("❌ Problem not saved.")
            input("Press Enter to continue...")
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")