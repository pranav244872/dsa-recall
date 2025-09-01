"""
Database manager for DSA Recall application.

This module provides high-level database operations for managing
DSA problems and tracking review streaks.
"""

import sqlite3
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from src.config import get_db_path
from .models import Problem, create_database_schema, problem_from_row


class DatabaseManager:
    """
    Manages database operations for the DSA Recall application.
    
    Provides methods for CRUD operations on problems, streak tracking,
    and spaced repetition functionality.
    """
    
    def __init__(self):
        """Initialize database manager and create schema if needed."""
        self.db_path = get_db_path()
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            create_database_schema(cursor)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection with row factory
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_problem(self, problem: Problem) -> int:
        """
        Add a new problem to the database.
        
        Args:
            problem: Problem instance to add
            
        Returns:
            int: ID of the newly created problem
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO problems (title, link, approach, code, streak_level, next_review, last_marked, history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                problem.title,
                problem.link,
                problem.approach,
                problem.code,
                problem.streak_level,
                problem.next_review.isoformat() if problem.next_review else None,
                problem.last_marked.isoformat() if problem.last_marked else None,
                problem.history
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_problem(self, problem_id: int) -> Optional[Problem]:
        """
        Retrieve a problem by ID.
        
        Args:
            problem_id: ID of the problem to retrieve
            
        Returns:
            Problem instance if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
            row = cursor.fetchone()
            return problem_from_row(row) if row else None
    
    def get_all_problems(self) -> List[Problem]:
        """
        Retrieve all problems from the database.
        
        Returns:
            List of all Problem instances
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM problems ORDER BY id')
            return [problem_from_row(row) for row in cursor.fetchall()]
    
    def get_due_problems(self, target_date: date = None) -> List[Problem]:
        """
        Retrieve problems that are due for review.
        
        Args:
            target_date: Date to check for due problems (defaults to today)
            
        Returns:
            List of Problem instances due for review
        """
        if target_date is None:
            target_date = date.today()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM problems WHERE next_review <= ? ORDER BY next_review',
                (target_date.isoformat(),)
            )
            return [problem_from_row(row) for row in cursor.fetchall()]
    
    def get_overdue_problems(self) -> List[Problem]:
        """
        Retrieve problems that are overdue (due before today).
        
        Returns:
            List of overdue Problem instances
        """
        today = date.today()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM problems WHERE next_review < ?',
                (today.isoformat(),)
            )
            return [problem_from_row(row) for row in cursor.fetchall()]
    
    def update_problem(self, problem: Problem) -> None:
        """
        Update an existing problem in the database.
        
        Args:
            problem: Problem instance with updated data
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE problems 
                SET title = ?, link = ?, approach = ?, code = ?, 
                    streak_level = ?, next_review = ?, last_marked = ?, history = ?
                WHERE id = ?
            ''', (
                problem.title,
                problem.link,
                problem.approach,
                problem.code,
                problem.streak_level,
                problem.next_review.isoformat() if problem.next_review else None,
                problem.last_marked.isoformat() if problem.last_marked else None,
                problem.history,
                problem.id
            ))
            conn.commit()
    
    def delete_problem(self, problem_id: int) -> bool:
        """
        Delete a problem from the database.
        
        Args:
            problem_id: ID of the problem to delete
            
        Returns:
            bool: True if problem was deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM problems WHERE id = ?', (problem_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def record_daily_review(self, review_date: date = None, count: int = 1) -> None:
        """
        Record that problems were reviewed on a specific date.
        
        Args:
            review_date: Date of review (defaults to today)
            count: Number of problems reviewed (defaults to 1)
        """
        if review_date is None:
            review_date = date.today()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO streak_tracker (date, problems_reviewed)
                VALUES (?, COALESCE((SELECT problems_reviewed FROM streak_tracker WHERE date = ?), 0) + ?)
            ''', (review_date.isoformat(), review_date.isoformat(), count))
            conn.commit()
    
    def get_streak_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get streak data for the last N days.
        
        Args:
            days: Number of days to retrieve (defaults to 30)
            
        Returns:
            List of dictionaries with date and problems_reviewed
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, problems_reviewed 
                FROM streak_tracker 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            return [{'date': row['date'], 'problems_reviewed': row['problems_reviewed']} 
                    for row in cursor.fetchall()]
    
    def get_current_streak(self) -> int:
        """
        Calculate the current consecutive streak of days with reviews.
        
        Returns:
            int: Number of consecutive days with at least one review
        """
        streak = 0
        current_date = date.today()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            while True:
                cursor.execute(
                    'SELECT problems_reviewed FROM streak_tracker WHERE date = ?',
                    (current_date.isoformat(),)
                )
                row = cursor.fetchone()
                
                if row and row['problems_reviewed'] > 0:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
        
        return streak
