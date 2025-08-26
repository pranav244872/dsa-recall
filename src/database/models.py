"""
Data models for the DSA Recall application.

This module defines the Problem data model and provides
database schema creation functionality.
"""

import json
import sqlite3
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Problem:
    """
    Represents a DSA problem with spaced repetition metadata.
    
    Attributes:
        id: Unique identifier (auto-generated)
        title: Problem title
        link: URL or reference link to the problem
        approach: Detailed explanation of the solution approach
        code: Code implementation
        streak_level: Current streak level for spaced repetition
        next_review: Date when the problem should be reviewed next
        last_marked: Date when the problem was last reviewed (None if never)
        history: JSON string containing review history
    """
    id: Optional[int] = None
    title: str = ""
    link: str = ""
    approach: str = ""
    code: str = ""
    streak_level: int = 1
    next_review: Optional[date] = None
    last_marked: Optional[date] = None
    history: str = "[]"  # JSON string of review history
    
    @property
    def history_list(self) -> List[Dict[str, Any]]:
        """
        Parse history JSON string into a list of dictionaries.
        
        Returns:
            List of history entries with date and status
        """
        try:
            return json.loads(self.history)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @history_list.setter
    def history_list(self, value: List[Dict[str, Any]]) -> None:
        """
        Set history from a list of dictionaries.
        
        Args:
            value: List of history entries to serialize to JSON
        """
        self.history = json.dumps(value, default=str)
    
    def add_history_entry(self, status: str, review_date: date = None) -> None:
        """
        Add a new entry to the review history.
        
        Args:
            status: Review status ('easy', 'hard', 'auto-hard')
            review_date: Date of review (defaults to today)
        """
        if review_date is None:
            review_date = date.today()
        
        history = self.history_list
        history.append({
            'date': review_date.isoformat(),
            'status': status
        })
        self.history_list = history


def create_database_schema(cursor: sqlite3.Cursor) -> None:
    """
    Create the database schema for the DSA Recall application.
    
    Args:
        cursor: SQLite cursor for executing SQL commands
    """
    # Create problems table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT,
            approach TEXT,
            code TEXT,
            streak_level INTEGER DEFAULT 1,
            next_review DATE,
            last_marked DATE,
            history TEXT DEFAULT '[]'
        )
    ''')
    
    # Create index on next_review for efficient querying of due problems
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_next_review ON problems(next_review)
    ''')
    
    # Create streak_tracker table for daily statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streak_tracker (
            date DATE PRIMARY KEY,
            problems_reviewed INTEGER DEFAULT 0
        )
    ''')


def problem_from_row(row: sqlite3.Row) -> Problem:
    """
    Convert a database row to a Problem object.
    
    Args:
        row: SQLite row from problems table
        
    Returns:
        Problem instance populated with row data
    """
    return Problem(
        id=row['id'],
        title=row['title'],
        link=row['link'],
        approach=row['approach'],
        code=row['code'],
        streak_level=row['streak_level'],
        next_review=datetime.strptime(row['next_review'], '%Y-%m-%d').date() if row['next_review'] else None,
        last_marked=datetime.strptime(row['last_marked'], '%Y-%m-%d').date() if row['last_marked'] else None,
        history=row['history']
    )