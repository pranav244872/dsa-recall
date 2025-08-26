"""
Streak Tracker window for DSA Recall GUI.

This window shows daily streak statistics and review history.
"""

from datetime import date, timedelta


def clear_screen():
    """Clear the screen for a cleaner interface."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_streak_tracker_window(db_manager):
    """
    Show the streak tracker window.
    
    Args:
        db_manager: Database manager instance
    """
    clear_screen()
    
    print("🔥 Streak Tracker")
    print("=" * 30)
    print()
    
    # Get streak data
    current_streak = db_manager.get_current_streak()
    streak_data = db_manager.get_streak_data(days=14)
    
    # Calculate total problems reviewed
    total_reviewed = sum(day_data.get("problems_reviewed", 0) for day_data in streak_data)
    
    # Display current streak
    print(f"Current Streak: 🔥 {current_streak} day{'s' if current_streak != 1 else ''}")
    print(f"Total problems reviewed in last 14 days: {total_reviewed}")
    print()
    
    # Create data lookup
    data_lookup = {}
    for day_data in streak_data:
        day_date = day_data["date"]
        data_lookup[day_date] = day_data.get("problems_reviewed", 0)
    
    # Show recent activity
    print("Recent Activity (Last 14 Days):")
    print("-" * 40)
    
    today = date.today()
    for i in range(13, -1, -1):  # 14 days including today, reverse order
        check_date = today - timedelta(days=i)
        activity_count = data_lookup.get(check_date, 0)
        
        # Format date and activity
        date_str = check_date.strftime("%Y-%m-%d (%a)")
        
        # Choose indicator based on activity
        if activity_count == 0:
            activity_indicator = "⚫"  # No activity
            activity_text = "No problems reviewed"
        elif activity_count <= 2:
            activity_indicator = "🟡"  # Light activity
            activity_text = f"{activity_count} problem{'s' if activity_count != 1 else ''} reviewed"
        elif activity_count <= 4:
            activity_indicator = "🟠"  # Medium activity
            activity_text = f"{activity_count} problems reviewed"
        else:
            activity_indicator = "🟢"  # High activity
            activity_text = f"{activity_count} problems reviewed"
        
        print(f"{activity_indicator} {date_str}: {activity_text}")
    
    print()
    print("Legend:")
    print("🟢 5+ problems  🟠 3-4 problems  🟡 1-2 problems  ⚫ No activity")
    print()
    
    input("Press Enter to continue...")