"""
Review dashboard screen for DSA Recall application.

This screen shows problems that are due for review and allows
navigation to individual problem review screens.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, ListItem, ListView, DataTable
from textual.binding import Binding
from datetime import date


class ReviewDashboardScreen(Screen):
    """
    Dashboard for reviewing due problems.
    
    Shows a list of problems that are due for review today
    and provides navigation to individual problem review screens.
    """
    
    CSS = """
    ReviewDashboardScreen {
        padding: 2;
        background: $surface;
    }
    
    .header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 2 0;
    }
    
    .stats {
        text-align: center;
        color: $text-muted;
        margin: 0 0 2 0;
    }
    
    .table-container {
        height: 1fr;
        border: tall $primary;
        background: $panel;
    }
    
    DataTable {
        height: 100%;
    }
    
    .no-problems {
        text-align: center;
        color: $text-muted;
        margin: 4 0;
        text-style: italic;
    }
    
    .shortcuts {
        text-align: center;
        color: $text-muted;
        margin: 2 0 0 0;
    }
    """
    
    BINDINGS = [
        Binding("enter", "review_selected", "Review"),
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize review dashboard screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.due_problems = []
    
    def compose(self) -> ComposeResult:
        """Compose the review dashboard layout."""
        with Vertical():
            yield Static("📅 Review Due Problems", classes="header")
            yield Static("", id="stats", classes="stats")
            
            with Vertical(classes="table-container"):
                table = DataTable(id="problems_table")
                table.add_columns("ID", "Title", "Streak", "Due Date", "Days Overdue")
                yield table
            
            yield Static(
                "Enter: Review Selected | R: Refresh | Esc: Back",
                classes="shortcuts"
            )
    
    def on_mount(self) -> None:
        """Load data when screen is mounted."""
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh the list of due problems."""
        self.due_problems = self.db.get_due_problems()
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current due problems."""
        stats = self.query_one("#stats", Static)
        table = self.query_one("#problems_table", DataTable)
        
        # Update stats
        today = date.today()
        if self.due_problems:
            overdue_count = sum(1 for p in self.due_problems if p.next_review < today)
            due_today_count = sum(1 for p in self.due_problems if p.next_review == today)
            
            stats_text = f"Total: {len(self.due_problems)} problems | "
            if due_today_count > 0:
                stats_text += f"Due today: {due_today_count} | "
            if overdue_count > 0:
                stats_text += f"Overdue: {overdue_count}"
            
            stats.update(stats_text)
        else:
            stats.update("No problems due for review today! 🎉")
        
        # Clear and populate table
        table.clear()
        
        if self.due_problems:
            for problem in self.due_problems:
                days_overdue = (today - problem.next_review).days
                days_overdue_str = f"{days_overdue}" if days_overdue > 0 else "0"
                
                table.add_row(
                    str(problem.id),
                    problem.title[:40] + "..." if len(problem.title) > 40 else problem.title,
                    str(problem.streak_level),
                    problem.next_review.strftime("%Y-%m-%d"),
                    days_overdue_str
                )
            
            # Focus the table
            table.focus()
        else:
            # Show empty state message
            table.add_row("No problems due", "", "", "", "")
    
    def action_review_selected(self) -> None:
        """Review the selected problem."""
        table = self.query_one("#problems_table", DataTable)
        
        if not self.due_problems:
            self.app.notify("No problems available for review", severity="information")
            return
        
        if table.cursor_row >= 0 and table.cursor_row < len(self.due_problems):
            selected_problem = self.due_problems[table.cursor_row]
            self.app.go_to_problem_review(selected_problem)
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the due problems list."""
        self.refresh_data()
        self.app.notify("Review list refreshed", severity="information")
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle table row selection."""
        if self.due_problems and event.row_index < len(self.due_problems):
            selected_problem = self.due_problems[event.row_index]
            self.app.go_to_problem_review(selected_problem)