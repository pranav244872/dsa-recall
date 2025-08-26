#!/usr/bin/env python3
"""
Simple test script for database functionality
"""

import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import DatabaseManager
from database.models import Problem
from utils.spaced_repetition import initialize_new_problem

def test_database():
    """Test basic database functionality"""
    print("Testing database functionality...")
    
    # Initialize database manager
    db = DatabaseManager()
    print("✓ Database initialized")
    
    # Create a test problem
    problem = Problem(
        title="Two Sum",
        link="https://leetcode.com/problems/two-sum/",
        approach="Use a hash map to store complements",
        code="def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i"
    )
    
    # Initialize spaced repetition metadata
    initialize_new_problem(problem)
    print("✓ Problem created with SR metadata")
    
    # Add to database
    problem_id = db.add_problem(problem)
    print(f"✓ Problem added with ID: {problem_id}")
    
    # Retrieve the problem
    retrieved = db.get_problem(problem_id)
    assert retrieved is not None
    assert retrieved.title == "Two Sum"
    print("✓ Problem retrieved successfully")
    
    # Test getting all problems
    all_problems = db.get_all_problems()
    assert len(all_problems) >= 1
    print(f"✓ Retrieved {len(all_problems)} problem(s)")
    
    # Test getting due problems
    due_problems = db.get_due_problems()
    print(f"✓ Found {len(due_problems)} due problem(s)")
    
    # Test streak tracking
    db.record_daily_review()
    streak = db.get_current_streak()
    print(f"✓ Current streak: {streak} day(s)")
    
    print("\nAll database tests passed! 🎉")

if __name__ == "__main__":
    test_database()