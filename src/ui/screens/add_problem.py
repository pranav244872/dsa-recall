"""
Add problem screen for DSA Recall application.

This screen allows users to add new DSA problems with title, link,
approach, and code using external editor integration.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen
from textual.widgets import Static, Input, Button
from textual.binding import Binding

from src.database.models import Problem
from src.utils.spaced_repetition import initialize_new_problem
from src.utils.editor import edit_approach, edit_code


class AddProblemScreen(Screen):
    """
    Screen for adding new DSA problems.
    
    Provides form inputs for problem details and integrates with
    external editor for long text content.
    """
    
    CSS = """
    AddProblemScreen {
        padding: 2;
        background: $surface;
    }
    
    .header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 2 0;
    }
    
    .form-container {
        max-width: 80;
        margin: 0 auto;
        border: tall $primary;
        background: $panel;
        padding: 2;
    }
    
    .field-label {
        text-style: bold;
        margin: 1 0 0 0;
    }
    
    .field-input {
        margin: 0 0 1 0;
        width: 100%;
    }
    
    .editor-info {
        color: $text-muted;
        margin: 0 0 1 0;
        text-style: italic;
    }
    
    .button-container {
        margin: 2 0 0 0;
        height: auto;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    .shortcuts {
        text-align: center;
        color: $text-muted;
        margin: 2 0 0 0;
    }
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save_problem", "Save"),
        Binding("ctrl+a", "edit_approach", "Edit Approach"),
        Binding("ctrl+c", "edit_code", "Edit Code"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize add problem screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.problem = Problem()  # New empty problem
        
    def compose(self) -> ComposeResult:
        """Compose the add problem form layout."""
        with Vertical():
            yield Static("➕ Add New DSA Problem", classes="header")
            
            with Container(classes="form-container"):
                # Title field
                yield Static("Title:", classes="field-label")
                yield Input(
                    placeholder="Enter problem title (e.g., Two Sum)",
                    id="title_input",
                    classes="field-input"
                )
                
                # Link field
                yield Static("Link:", classes="field-label")
                yield Input(
                    placeholder="Enter problem URL or reference",
                    id="link_input",
                    classes="field-input"
                )
                
                # Approach section
                yield Static("Approach:", classes="field-label")
                yield Static(
                    "Click 'Edit Approach' button or press Ctrl+A to open external editor",
                    classes="editor-info"
                )
                yield Static("", id="approach_preview", classes="editor-info")
                
                # Code section
                yield Static("Code:", classes="field-label")
                yield Static(
                    "Click 'Edit Code' button or press Ctrl+C to open external editor",
                    classes="editor-info"
                )
                yield Static("", id="code_preview", classes="editor-info")
                
                # Buttons
                with Horizontal(classes="button-container"):
                    yield Button("Edit Approach", id="approach_button", variant="primary")
                    yield Button("Edit Code", id="code_button", variant="primary")
                    yield Button("Save Problem", id="save_button", variant="success")
                    yield Button("Cancel", id="cancel_button", variant="error")
            
            yield Static(
                "Ctrl+A: Edit Approach | Ctrl+C: Edit Code | Ctrl+S: Save | Esc: Back",
                classes="shortcuts"
            )
    
    def on_mount(self) -> None:
        """Set focus when screen is mounted."""
        self.query_one("#title_input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "approach_button":
            self.action_edit_approach()
        elif event.button.id == "code_button":
            self.action_edit_code()
        elif event.button.id == "save_button":
            self.action_save_problem()
        elif event.button.id == "cancel_button":
            self.action_go_back()
    
    def action_edit_approach(self) -> None:
        """Open external editor for approach."""
        try:
            edited_approach = edit_approach(self.problem.approach)
            if edited_approach is not None:
                self.problem.approach = edited_approach
                # Update preview
                preview = self.query_one("#approach_preview", Static)
                if edited_approach.strip():
                    lines = edited_approach.strip().split('\n')
                    preview_text = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
                    if len(lines) > 1:
                        preview_text += f" (+{len(lines)-1} more lines)"
                    preview.update(f"✓ Approach added: {preview_text}")
                else:
                    preview.update("(No approach)")
        except Exception as e:
            self.app.notify_error(f"Failed to open editor: {str(e)}")
    
    def action_edit_code(self) -> None:
        """Open external editor for code."""
        try:
            edited_code = edit_code(self.problem.code)
            if edited_code is not None:
                self.problem.code = edited_code
                # Update preview
                preview = self.query_one("#code_preview", Static)
                if edited_code.strip():
                    lines = edited_code.strip().split('\n')
                    preview_text = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
                    if len(lines) > 1:
                        preview_text += f" (+{len(lines)-1} more lines)"
                    preview.update(f"✓ Code added: {preview_text}")
                else:
                    preview.update("(No code)")
        except Exception as e:
            self.app.notify_error(f"Failed to open editor: {str(e)}")
    
    def action_save_problem(self) -> None:
        """Save the new problem to database."""
        # Get form data
        title = self.query_one("#title_input", Input).value.strip()
        link = self.query_one("#link_input", Input).value.strip()
        
        # Validate
        if not title:
            self.app.notify_error("Please enter a problem title")
            self.query_one("#title_input", Input).focus()
            return
        
        # Update problem with form data
        self.problem.title = title
        self.problem.link = link
        
        # Initialize spaced repetition metadata
        initialize_new_problem(self.problem)
        
        try:
            # Save to database
            problem_id = self.db.add_problem(self.problem)
            self.app.notify_success(f"Problem '{title}' added successfully!")
            
            # Reset form
            self._reset_form()
            
            # Go back to main menu
            self.app.pop_screen()
            
        except Exception as e:
            self.app.notify_error(f"Failed to save problem: {str(e)}")
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def _reset_form(self) -> None:
        """Reset the form to empty state."""
        self.problem = Problem()
        self.query_one("#title_input", Input).value = ""
        self.query_one("#link_input", Input).value = ""
        self.query_one("#approach_preview", Static).update("")
        self.query_one("#code_preview", Static).update("")
    
    def refresh_data(self) -> None:
        """Refresh screen data (reset form when returning to this screen)."""
        self._reset_form()