"""
Problem review screen for DSA Recall application.

This screen displays a single problem with collapsible approach/code
sections and allows marking as easy or hard for spaced repetition.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.binding import Binding

from src.utils.spaced_repetition import mark_problem_easy, mark_problem_hard
from ..widgets.collapsible_text import ProblemDetails


class ProblemReviewScreen(Screen):
    """
    Screen for reviewing individual problems.
    
    Shows problem details with collapsible sections and provides
    options to mark as easy or hard for spaced repetition.
    """
    
    CSS = """
    ProblemReviewScreen {
        padding: 2;
        background: $surface;
    }
    
    .header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 2 0;
    }
    
    .problem-container {
        height: 1fr;
        margin: 0 0 2 0;
    }
    
    .button-container {
        height: auto;
        padding: 1;
        background: $panel;
        border: tall $primary;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    .easy-button {
        background: $success;
    }
    
    .hard-button {
        background: $error;
    }
    
    .shortcuts {
        text-align: center;
        color: $text-muted;
        margin: 1 0 0 0;
    }
    
    .review-info {
        text-align: center;
        color: $text-muted;
        margin: 0 0 1 0;
        text-style: italic;
    }
    """
    
    BINDINGS = [
        Binding("a", "toggle_approach", "Toggle Approach"),
        Binding("c", "toggle_code", "Toggle Code"),
        Binding("e", "mark_easy", "Mark Easy"),
        Binding("h", "mark_hard", "Mark Hard"),
        Binding("escape", "go_back", "Back"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize problem review screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.problem = None
    
    def compose(self) -> ComposeResult:
        """Compose the problem review layout."""
        with Vertical():
            yield Static("📖 Problem Review", classes="header")
            yield Static("", id="review_info", classes="review-info")
            
            # Problem details container
            with Vertical(classes="problem-container"):
                yield ProblemDetails(self.problem, id="problem_details")
            
            # Action buttons
            with Horizontal(classes="button-container"):
                yield Button("🟢 Mark Easy", id="easy_button", classes="easy-button")
                yield Button("🔴 Mark Hard", id="hard_button", classes="hard-button")
                yield Button("↩️ Back", id="back_button")
            
            yield Static(
                "[a] Toggle Approach | [c] Toggle Code | [e] Mark Easy | [h] Mark Hard | [←] Back",
                classes="shortcuts"
            )
    
    def set_problem(self, problem):
        """
        Set the problem to be reviewed.
        
        Args:
            problem: Problem instance to review
        """
        self.problem = problem
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current problem."""
        if not self.problem:
            return
        
        # Update review info
        review_info = self.query_one("#review_info", Static)
        info_text = f"Streak Level: {self.problem.streak_level} | "
        if self.problem.last_marked:
            info_text += f"Last Reviewed: {self.problem.last_marked}"
        else:
            info_text += "Never reviewed"
        review_info.update(info_text)
        
        # Update problem details
        problem_details = self.query_one("#problem_details", ProblemDetails)
        problem_details.update_problem(self.problem)
    
    def on_mount(self) -> None:
        """Set focus when screen is mounted."""
        if self.problem:
            self._update_display()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "easy_button":
            self.action_mark_easy()
        elif event.button.id == "hard_button":
            self.action_mark_hard()
        elif event.button.id == "back_button":
            self.action_go_back()
    
    def action_toggle_approach(self) -> None:
        """Toggle approach visibility."""
        # This will be handled by the ProblemDetails widget
        # which has its own key bindings
        pass
    
    def action_toggle_code(self) -> None:
        """Toggle code visibility."""
        # This will be handled by the ProblemDetails widget
        # which has its own key bindings
        pass
    
    def action_mark_easy(self) -> None:
        """Mark the problem as easy."""
        if not self.problem:
            return
        
        try:
            # Apply spaced repetition logic
            old_streak = self.problem.streak_level
            mark_problem_easy(self.problem)
            
            # Update in database
            self.db.update_problem(self.problem)
            
            # Record daily review
            self.db.record_daily_review()
            
            # Show success message
            new_streak = self.problem.streak_level
            next_review = self.problem.next_review
            self.app.notify_success(
                f"Marked as Easy! Streak: {old_streak} → {new_streak}. "
                f"Next review: {next_review}"
            )
            
            # Go back to review dashboard
            self.app.pop_screen()
            
        except Exception as e:
            self.app.notify_error(f"Failed to mark as easy: {str(e)}")
    
    def action_mark_hard(self) -> None:
        """Mark the problem as hard."""
        if not self.problem:
            return
        
        try:
            # Apply spaced repetition logic
            old_streak = self.problem.streak_level
            mark_problem_hard(self.problem)
            
            # Update in database
            self.db.update_problem(self.problem)
            
            # Record daily review
            self.db.record_daily_review()
            
            # Show message
            next_review = self.problem.next_review
            self.app.notify_warning(
                f"Marked as Hard. Streak reset to 1. Next review: {next_review}"
            )
            
            # Go back to review dashboard
            self.app.pop_screen()
            
        except Exception as e:
            self.app.notify_error(f"Failed to mark as hard: {str(e)}")
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def refresh_data(self) -> None:
        """Refresh screen data."""
        if self.problem:
            # Reload problem from database to get latest data
            updated_problem = self.db.get_problem(self.problem.id)
            if updated_problem:
                self.problem = updated_problem
                self._update_display()