"""
All problems browser screen for DSA Recall application.

This screen shows all problems in a table format and allows
viewing, editing, and deleting problems.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, DataTable, Button
from textual.binding import Binding
from datetime import date


class AllProblemsScreen(Screen):
    """
    Browser for viewing all problems.
    
    Shows all problems in a table with options to view, edit, or delete.
    """
    
    CSS = """
    AllProblemsScreen {
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
    
    .button-container {
        height: auto;
        padding: 1;
        background: $panel;
        border: tall $primary;
        margin: 1 0 0 0;
    }
    
    Button {
        margin: 0 1;
        min-width: 12;
    }
    
    .shortcuts {
        text-align: center;
        color: $text-muted;
        margin: 1 0 0 0;
    }
    
    .no-problems {
        text-align: center;
        color: $text-muted;
        margin: 4 0;
        text-style: italic;
    }
    """
    
    BINDINGS = [
        Binding("enter", "view_selected", "View"),
        Binding("E", "edit_selected", "Edit"),
        Binding("D", "delete_selected", "Delete"),
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize all problems screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.all_problems = []
        self.confirm_delete = False
        self.delete_problem_id = None
    
    def compose(self) -> ComposeResult:
        """Compose the all problems layout."""
        with Vertical():
            yield Static("📖 All Problems", classes="header")
            yield Static("", id="stats", classes="stats")
            
            with Vertical(classes="table-container"):
                table = DataTable(id="problems_table")
                table.add_columns("ID", "Title", "Next Review", "Streak", "Status")
                yield table
            
            with Horizontal(classes="button-container"):
                yield Button("👁️ View", id="view_button")
                yield Button("✏️ Edit", id="edit_button")
                yield Button("🗑️ Delete", id="delete_button")
                yield Button("↩️ Back", id="back_button")
            
            yield Static(
                "Enter: View | E: Edit | D: Delete | R: Refresh | Esc: Back",
                classes="shortcuts"
            )
    
    def on_mount(self) -> None:
        """Load data when screen is mounted."""
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh the list of all problems."""
        self.all_problems = self.db.get_all_problems()
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current problems."""
        stats = self.query_one("#stats", Static)
        table = self.query_one("#problems_table", DataTable)
        
        # Update stats
        if self.all_problems:
            today = date.today()
            due_count = sum(1 for p in self.all_problems if p.next_review and p.next_review <= today)
            avg_streak = sum(p.streak_level for p in self.all_problems) / len(self.all_problems)
            
            stats_text = f"Total: {len(self.all_problems)} problems | "
            stats_text += f"Due: {due_count} | Average streak: {avg_streak:.1f}"
            stats.update(stats_text)
        else:
            stats.update("No problems found. Add some problems first!")
        
        # Clear and populate table
        table.clear()
        
        if self.all_problems:
            today = date.today()
            for problem in self.all_problems:
                # Determine status
                if not problem.next_review:
                    status = "New"
                elif problem.next_review <= today:
                    days_overdue = (today - problem.next_review).days
                    if days_overdue > 0:
                        status = f"Overdue ({days_overdue}d)"
                    else:
                        status = "Due"
                else:
                    days_until = (problem.next_review - today).days
                    status = f"Due in {days_until}d"
                
                table.add_row(
                    str(problem.id),
                    problem.title[:35] + "..." if len(problem.title) > 35 else problem.title,
                    problem.next_review.strftime("%Y-%m-%d") if problem.next_review else "N/A",
                    str(problem.streak_level),
                    status
                )
            
            # Focus the table
            table.focus()
        else:
            # Show empty state message
            table.add_row("No problems found", "", "", "", "")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "view_button":
            self.action_view_selected()
        elif event.button.id == "edit_button":
            self.action_edit_selected()
        elif event.button.id == "delete_button":
            self.action_delete_selected()
        elif event.button.id == "back_button":
            self.action_go_back()
    
    def action_view_selected(self) -> None:
        """View the selected problem."""
        selected_problem = self._get_selected_problem()
        if selected_problem:
            self.app.go_to_problem_review(selected_problem)
    
    def action_edit_selected(self) -> None:
        """Edit the selected problem."""
        selected_problem = self._get_selected_problem()
        if selected_problem:
            self.app.go_to_edit_problem(selected_problem)
    
    def action_delete_selected(self) -> None:
        """Delete the selected problem."""
        selected_problem = self._get_selected_problem()
        if not selected_problem:
            return
        
        if not self.confirm_delete:
            # First press - show confirmation
            self.confirm_delete = True
            self.delete_problem_id = selected_problem.id
            self.app.notify_warning(
                f"Press D again to confirm deletion of '{selected_problem.title}'"
            )
        elif self.delete_problem_id == selected_problem.id:
            # Second press - confirm deletion
            try:
                self.db.delete_problem(selected_problem.id)
                self.app.notify_success(f"Problem '{selected_problem.title}' deleted")
                self.refresh_data()
                self.confirm_delete = False
                self.delete_problem_id = None
            except Exception as e:
                self.app.notify_error(f"Failed to delete problem: {str(e)}")
        else:
            # Different problem selected - reset confirmation
            self.confirm_delete = True
            self.delete_problem_id = selected_problem.id
            self.app.notify_warning(
                f"Press D again to confirm deletion of '{selected_problem.title}'"
            )
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the problems list."""
        self.refresh_data()
        self.app.notify("Problems list refreshed", severity="information")
    
    def _get_selected_problem(self):
        """Get the currently selected problem."""
        table = self.query_one("#problems_table", DataTable)
        
        if not self.all_problems:
            self.app.notify("No problems available", severity="information")
            return None
        
        if table.cursor_row >= 0 and table.cursor_row < len(self.all_problems):
            return self.all_problems[table.cursor_row]
        
        self.app.notify("Please select a problem", severity="information")
        return None
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle table row selection."""
        if self.all_problems and event.row_index < len(self.all_problems):
            selected_problem = self.all_problems[event.row_index]
            self.app.go_to_problem_review(selected_problem)