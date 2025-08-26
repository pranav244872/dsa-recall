"""
Spaced repetition algorithm implementation.

This module contains the core logic for calculating review intervals
and managing the spaced repetition system.
"""

from datetime import date, timedelta
from typing import Tuple

from src.config import INITIAL_STREAK_LEVEL, INITIAL_INTERVAL_DAYS, STREAK_MULTIPLIER
from src.database.models import Problem


def calculate_next_review_date(streak_level: int, mark_as_easy: bool = True) -> date:
    """
    Calculate the next review date based on spaced repetition algorithm.
    
    The algorithm uses exponential backoff:
    - Easy: next_review = today + 2^streak_level days
    - Hard: streak_level resets to 1, next_review = tomorrow
    
    Args:
        streak_level: Current streak level
        mark_as_easy: True for easy review, False for hard review
        
    Returns:
        date: Next review date
    """
    today = date.today()
    
    if mark_as_easy:
        # Easy review: increase interval exponentially
        interval_days = STREAK_MULTIPLIER ** streak_level
        return today + timedelta(days=interval_days)
    else:
        # Hard review: reset to shortest interval
        return today + timedelta(days=INITIAL_INTERVAL_DAYS)


def mark_problem_easy(problem: Problem) -> None:
    """
    Mark a problem as easy and update spaced repetition metadata.
    
    Args:
        problem: Problem instance to update
    """
    # Increase streak level
    problem.streak_level += 1
    
    # Calculate next review date
    problem.next_review = calculate_next_review_date(problem.streak_level, mark_as_easy=True)
    
    # Update last marked date
    problem.last_marked = date.today()
    
    # Add to history
    problem.add_history_entry("easy")


def mark_problem_hard(problem: Problem) -> None:
    """
    Mark a problem as hard and reset spaced repetition metadata.
    
    Args:
        problem: Problem instance to update
    """
    # Reset streak level
    problem.streak_level = INITIAL_STREAK_LEVEL
    
    # Calculate next review date (short interval)
    problem.next_review = calculate_next_review_date(problem.streak_level, mark_as_easy=False)
    
    # Update last marked date
    problem.last_marked = date.today()
    
    # Add to history
    problem.add_history_entry("hard")


def auto_mark_overdue_problems(problems: list[Problem]) -> int:
    """
    Automatically mark overdue problems as hard.
    
    Problems that are overdue (next_review < yesterday) are automatically
    marked as hard to reset their spaced repetition interval.
    
    Args:
        problems: List of overdue problems
        
    Returns:
        int: Number of problems marked as auto-hard
    """
    count = 0
    yesterday = date.today() - timedelta(days=1)
    
    for problem in problems:
        if problem.next_review and problem.next_review < yesterday:
            # Auto-mark as hard
            problem.streak_level = INITIAL_STREAK_LEVEL
            problem.next_review = calculate_next_review_date(problem.streak_level, mark_as_easy=False)
            problem.add_history_entry("auto-hard")
            count += 1
    
    return count


def get_streak_statistics(problem: Problem) -> dict:
    """
    Get statistics about a problem's review streak.
    
    Args:
        problem: Problem instance
        
    Returns:
        dict: Statistics including streak level, next review, etc.
    """
    total_reviews = len(problem.history_list)
    easy_reviews = sum(1 for entry in problem.history_list if entry['status'] == 'easy')
    hard_reviews = sum(1 for entry in problem.history_list if entry['status'] == 'hard')
    auto_hard_reviews = sum(1 for entry in problem.history_list if entry['status'] == 'auto-hard')
    
    days_until_review = (problem.next_review - date.today()).days if problem.next_review else 0
    
    return {
        'streak_level': problem.streak_level,
        'total_reviews': total_reviews,
        'easy_reviews': easy_reviews,
        'hard_reviews': hard_reviews,
        'auto_hard_reviews': auto_hard_reviews,
        'last_marked': problem.last_marked,
        'next_review': problem.next_review,
        'days_until_review': days_until_review,
        'is_overdue': days_until_review < 0
    }


def initialize_new_problem(problem: Problem) -> None:
    """
    Initialize spaced repetition metadata for a new problem.
    
    Args:
        problem: New problem instance to initialize
    """
    problem.streak_level = INITIAL_STREAK_LEVEL
    problem.next_review = date.today() + timedelta(days=INITIAL_INTERVAL_DAYS)
    problem.last_marked = None
    problem.history = "[]"