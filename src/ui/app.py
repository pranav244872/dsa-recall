"""
Main TUI application for DSA Recall.

This module contains the core Textual application class and screen management.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Header, Footer

from .screens.main_menu import MainMenuScreen
from .screens.add_problem import AddProblemScreen
from .screens.review_dashboard import ReviewDashboardScreen
from .screens.all_problems import AllProblemsScreen
from .screens.streak_tracker import StreakTrackerScreen
from .screens.problem_review import ProblemReviewScreen
from .screens.edit_problem import EditProblemScreen

from src.database.db_manager import DatabaseManager
from src.utils.spaced_repetition import auto_mark_overdue_problems
from src.config import APP_TITLE


class DSARecallApp(App):
    """
    Main DSA Recall application.
    
    Manages screens, database operations, and application state.
    """
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    Header {
        background: $primary;
        color: $text;
        dock: top;
        height: 1;
    }
    
    Footer {
        background: $primary;
        color: $text;
        dock: bottom;
        height: 1;
    }
    """
    
    TITLE = APP_TITLE
    SUB_TITLE = "Terminal-based Spaced Repetition for DSA Problems"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]
    
    # Reactive attributes for global state
    current_problem = reactive(None)
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.db = DatabaseManager()
        self._setup_screens()
        self._auto_mark_overdue_problems()
    
    def _setup_screens(self):
        """Install all application screens."""
        self.install_screen(MainMenuScreen(self.db), name="main_menu")
        self.install_screen(AddProblemScreen(self.db), name="add_problem")
        self.install_screen(ReviewDashboardScreen(self.db), name="review_dashboard")
        self.install_screen(AllProblemsScreen(self.db), name="all_problems")
        self.install_screen(StreakTrackerScreen(self.db), name="streak_tracker")
        self.install_screen(ProblemReviewScreen(self.db), name="problem_review")
        self.install_screen(EditProblemScreen(self.db), name="edit_problem")
    
    def _auto_mark_overdue_problems(self):
        """Auto-mark overdue problems as hard on startup."""
        overdue_problems = self.db.get_overdue_problems()
        if overdue_problems:
            count = auto_mark_overdue_problems(overdue_problems)
            # Update problems in database
            for problem in overdue_problems:
                self.db.update_problem(problem)
            
            if count > 0:
                self.notify(f"Auto-marked {count} overdue problem(s) as hard", severity="warning")
    
    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Start with the main menu
        self.push_screen("main_menu")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def go_to_main_menu(self):
        """Navigate to the main menu."""
        self.switch_screen("main_menu")
    
    def go_to_add_problem(self):
        """Navigate to add problem screen."""
        self.push_screen("add_problem")
    
    def go_to_review_dashboard(self):
        """Navigate to review dashboard."""
        self.push_screen("review_dashboard")
    
    def go_to_all_problems(self):
        """Navigate to all problems browser."""
        self.push_screen("all_problems")
    
    def go_to_streak_tracker(self):
        """Navigate to streak tracker."""
        self.push_screen("streak_tracker")
    
    def go_to_problem_review(self, problem):
        """Navigate to problem review screen."""
        self.current_problem = problem
        # Get the screen and update it with the problem
        screen = self.get_screen("problem_review")
        screen.set_problem(problem)
        self.push_screen("problem_review")
    
    def go_to_edit_problem(self, problem):
        """Navigate to edit problem screen."""
        self.current_problem = problem
        # Get the screen and update it with the problem
        screen = self.get_screen("edit_problem")
        screen.set_problem(problem)
        self.push_screen("edit_problem")
    
    def refresh_current_screen(self):
        """Refresh the current screen (useful after data changes)."""
        current_screen = self.screen
        if hasattr(current_screen, 'refresh_data'):
            current_screen.refresh_data()
    
    def notify_success(self, message: str):
        """Show a success notification."""
        self.notify(message, severity="information")
    
    def notify_error(self, message: str):
        """Show an error notification."""
        self.notify(message, severity="error")
    
    def notify_warning(self, message: str):
        """Show a warning notification."""
        self.notify(message, severity="warning")


def run_app():
    """Run the DSA Recall application."""
    app = DSARecallApp()
    app.run()