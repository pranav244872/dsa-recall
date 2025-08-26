"""
Main menu screen for DSA Recall application.

This screen provides the primary navigation interface for the application.
"""

from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Static, ListItem, ListView
from textual.binding import Binding

from src.config import MAIN_MENU_OPTIONS


class MainMenuScreen(Screen):
    """
    Main menu screen with navigation options.
    
    Displays the main menu options and handles navigation to different
    parts of the application.
    """
    
    CSS = """
    MainMenuScreen {
        align: center middle;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 2 0;
    }
    
    .subtitle {
        text-align: center;
        color: $text-muted;
        margin: 0 0 3 0;
    }
    
    ListView {
        height: auto;
        max-height: 15;
        width: 60;
        border: tall $primary;
        background: $panel;
    }
    
    ListItem {
        padding: 1 2;
        margin: 0;
    }
    
    ListItem:hover {
        background: $accent 20%;
    }
    
    .help-text {
        text-align: center;
        color: $text-muted;
        margin: 2 0;
    }
    """
    
    BINDINGS = [
        Binding("enter", "select_option", "Select"),
        Binding("1", "select_1", "Add Problem"),
        Binding("2", "select_2", "Review Problems"),
        Binding("3", "select_3", "All Problems"),
        Binding("4", "select_4", "Streak Tracker"),
        Binding("5", "select_5", "Exit"),
        Binding("escape", "app.pop_screen", "Back"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize main menu screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
    
    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        with Center():
            with Middle():
                with Vertical():
                    yield Static("🧠 DSA Recall", classes="title")
                    yield Static("Spaced Repetition for DSA Problems", classes="subtitle")
                    
                    # Menu options
                    menu_items = []
                    for i, option in enumerate(MAIN_MENU_OPTIONS, 1):
                        menu_items.append(ListItem(Static(f"{i}. {option}"), name=str(i)))
                    
                    yield ListView(*menu_items, id="menu_list")
                    
                    yield Static(
                        "Use ↑↓ arrows and Enter to navigate, or press number keys",
                        classes="help-text"
                    )
    
    def on_mount(self) -> None:
        """Set focus when screen is mounted."""
        self.query_one("#menu_list", ListView).focus()
    
    def action_select_option(self) -> None:
        """Handle menu option selection."""
        menu_list = self.query_one("#menu_list", ListView)
        if menu_list.highlighted_child:
            option_index = int(menu_list.highlighted_child.name)
            self._handle_option_selection(option_index)
    
    def action_select_1(self) -> None:
        """Select option 1 (Add Problem)."""
        self._handle_option_selection(1)
    
    def action_select_2(self) -> None:
        """Select option 2 (Review Problems)."""
        self._handle_option_selection(2)
    
    def action_select_3(self) -> None:
        """Select option 3 (All Problems)."""
        self._handle_option_selection(3)
    
    def action_select_4(self) -> None:
        """Select option 4 (Streak Tracker)."""
        self._handle_option_selection(4)
    
    def action_select_5(self) -> None:
        """Select option 5 (Exit)."""
        self._handle_option_selection(5)
    
    def _handle_option_selection(self, option_index: int) -> None:
        """
        Handle menu option selection.
        
        Args:
            option_index: Selected option number (1-5)
        """
        if option_index == 1:
            # Add Problem
            self.app.go_to_add_problem()
        elif option_index == 2:
            # Review Due Problems
            due_problems = self.db.get_due_problems()
            if not due_problems:
                self.app.notify("No problems due for review today!", severity="information")
            else:
                self.app.go_to_review_dashboard()
        elif option_index == 3:
            # View All Problems
            all_problems = self.db.get_all_problems()
            if not all_problems:
                self.app.notify("No problems found. Add some problems first!", severity="information")
            else:
                self.app.go_to_all_problems()
        elif option_index == 4:
            # View Streak Tracker
            self.app.go_to_streak_tracker()
        elif option_index == 5:
            # Exit
            self.app.exit()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list view selection."""
        if event.item and event.item.name:
            option_index = int(event.item.name)
            self._handle_option_selection(option_index)
    
    def refresh_data(self) -> None:
        """Refresh screen data (called when returning to this screen)."""
        # Update any dynamic content if needed
        pass