"""
All Problems browser window for DSA Recall GUI.

This window shows a list of all problems with search and management options.
"""

from datetime import date


def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_all_problems_window(db_manager):
    """
    Show the all problems browser window.
    
    Args:
        db_manager: Database manager instance
    """
    while True:
        clear_screen()
        
        print("📖 All Problems")
        print("=" * 30)
        print()
        
        # Get all problems
        problems = db_manager.get_all_problems()
        
        if not problems:
            print("No problems found. Add some problems first!")
            input("Press Enter to continue...")
            return
        
        # Display problems in table format
        print(f"{'ID':<4} {'Title':<30} {'Streak':<6} {'Next Review':<12} {'Last Marked':<12}")
        print("-" * 70)
        
        for problem in problems:
            next_review = problem.next_review.strftime("%Y-%m-%d") if problem.next_review else "Not set"
            last_marked = problem.last_marked.strftime("%Y-%m-%d") if problem.last_marked else "Never"
            
            # Truncate title if too long
            title = problem.title[:28] + ".." if len(problem.title) > 30 else problem.title
            
            # Color coding for due/overdue problems
            today = date.today()
            status = "  "
            if problem.next_review:
                if problem.next_review <= today:
                    status = "📅"  # Due today
                elif problem.next_review < today:
                    status = "🔴"  # Overdue
            
            print(f"{problem.id:<4} {title:<30} {problem.streak_level:<6} {next_review:<12} {last_marked:<12} {status}")
        
        print("\nActions:")
        print("[v<ID>] View/Edit problem (e.g., v1)")
        print("[d<ID>] Delete problem (e.g., d1)")
        print("[r] Refresh list")
        print("[b] Back to main dashboard")
        
        try:
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == 'r':
                continue  # Refresh by looping
            elif choice.startswith('v'):
                # View problem
                try:
                    problem_id = int(choice[1:])
                    problem = db_manager.get_problem(problem_id)
                    if problem:
                        from .problem_card import show_problem_card_window
                        show_problem_card_window(db_manager, problem)
                    else:
                        print("Problem not found!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid problem ID!")
                    input("Press Enter to continue...")
            elif choice.startswith('d'):
                # Delete problem
                try:
                    problem_id = int(choice[1:])
                    problem = db_manager.get_problem(problem_id)
                    if problem:
                        confirm = input(f"Are you sure you want to delete '{problem.title}'? [y/N]: ").strip().lower()
                        if confirm in ['y', 'yes']:
                            success = db_manager.delete_problem(problem_id)
                            if success:
                                print(f"✅ Problem '{problem.title}' deleted successfully.")
                            else:
                                print("❌ Failed to delete problem.")
                            input("Press Enter to continue...")
                    else:
                        print("Problem not found!")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid problem ID!")
                    input("Press Enter to continue...")
            else:
                print("Invalid choice! Please try again.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            break