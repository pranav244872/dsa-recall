"""
Edit problem screen for DSA Recall application.

This screen allows users to edit existing DSA problems with
external editor integration for long text fields.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen
from textual.widgets import Static, Input, Button
from textual.binding import Binding

from src.utils.editor import edit_approach, edit_code


class EditProblemScreen(Screen):
    """
    Screen for editing existing DSA problems.
    
    Provides form inputs for problem details and integrates with
    external editor for long text content.
    """
    
    CSS = """
    EditProblemScreen {
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
    
    .editor-preview {
        color: $text-muted;
        margin: 0 0 1 0;
        background: $surface-lighten-1;
        padding: 1;
        border-left: thick $accent;
        max-height: 5;
        overflow-y: auto;
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
        Binding("ctrl+s", "save_changes", "Save"),
        Binding("t", "edit_title", "Edit Title"),
        Binding("l", "edit_link", "Edit Link"),
        Binding("a", "edit_approach", "Edit Approach"),
        Binding("c", "edit_code", "Edit Code"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize edit problem screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.problem = None
        self.original_problem = None
    
    def compose(self) -> ComposeResult:
        """Compose the edit problem form layout."""
        with Vertical():
            yield Static("✏️ Edit Problem", classes="header")
            yield Static("", id="problem_info", classes="editor-info")
            
            with Container(classes="form-container"):
                # Title field
                yield Static("Title:", classes="field-label")
                yield Input(
                    placeholder="Enter problem title",
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
                yield Static("", id="approach_preview", classes="editor-preview")
                
                # Code section
                yield Static("Code:", classes="field-label")
                yield Static("", id="code_preview", classes="editor-preview")
                
                # Buttons
                with Horizontal(classes="button-container"):
                    yield Button("[t] Edit Title", id="title_button", variant="primary")
                    yield Button("[l] Edit Link", id="link_button", variant="primary")
                    yield Button("[a] Edit Approach", id="approach_button", variant="primary")
                    yield Button("[c] Edit Code", id="code_button", variant="primary")
                
                with Horizontal(classes="button-container"):
                    yield Button("💾 Save Changes", id="save_button", variant="success")
                    yield Button("❌ Cancel", id="cancel_button", variant="error")
            
            yield Static(
                "[t] Edit Title | [l] Edit Link | [a] Edit Approach | [c] Edit Code | Ctrl+S: Save | Esc: Back",
                classes="shortcuts"
            )
    
    def set_problem(self, problem):
        """
        Set the problem to be edited.
        
        Args:
            problem: Problem instance to edit
        """
        self.problem = problem
        # Keep a copy of the original for comparison
        import copy
        self.original_problem = copy.deepcopy(problem)
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current problem data."""
        if not self.problem:
            return
        
        # Update problem info
        info = self.query_one("#problem_info", Static)
        info.update(f"Editing Problem #{self.problem.id}")
        
        # Update form fields
        self.query_one("#title_input", Input).value = self.problem.title
        self.query_one("#link_input", Input).value = self.problem.link
        
        # Update previews
        self._update_approach_preview()
        self._update_code_preview()
    
    def _update_approach_preview(self) -> None:
        """Update the approach preview."""
        preview = self.query_one("#approach_preview", Static)
        if self.problem.approach.strip():
            # Show first few lines of approach
            lines = self.problem.approach.strip().split('\n')[:3]
            preview_text = '\n'.join(lines)
            if len(self.problem.approach.strip().split('\n')) > 3:
                preview_text += "\n... (more content)"
            preview.update(preview_text)
        else:
            preview.update("(No approach set)")
    
    def _update_code_preview(self) -> None:
        """Update the code preview."""
        preview = self.query_one("#code_preview", Static)
        if self.problem.code.strip():
            # Show first few lines of code
            lines = self.problem.code.strip().split('\n')[:3]
            preview_text = '\n'.join(lines)
            if len(self.problem.code.strip().split('\n')) > 3:
                preview_text += "\n... (more content)"
            preview.update(preview_text)
        else:
            preview.update("(No code set)")
    
    def on_mount(self) -> None:
        """Set focus when screen is mounted."""
        if self.problem:
            self._update_display()
            self.query_one("#title_input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "title_button":
            self.action_edit_title()
        elif event.button.id == "link_button":
            self.action_edit_link()
        elif event.button.id == "approach_button":
            self.action_edit_approach()
        elif event.button.id == "code_button":
            self.action_edit_code()
        elif event.button.id == "save_button":
            self.action_save_changes()
        elif event.button.id == "cancel_button":
            self.action_go_back()
    
    def action_edit_title(self) -> None:
        """Focus on title input."""
        self.query_one("#title_input", Input).focus()
    
    def action_edit_link(self) -> None:
        """Focus on link input."""
        self.query_one("#link_input", Input).focus()
    
    def action_edit_approach(self) -> None:
        """Open external editor for approach."""
        if not self.problem:
            return
        
        try:
            edited_approach = edit_approach(self.problem.approach)
            if edited_approach is not None:
                self.problem.approach = edited_approach
                self._update_approach_preview()
                self.app.notify("Approach updated", severity="information")
        except Exception as e:
            self.app.notify_error(f"Failed to open editor: {str(e)}")
    
    def action_edit_code(self) -> None:
        """Open external editor for code."""
        if not self.problem:
            return
        
        try:
            edited_code = edit_code(self.problem.code)
            if edited_code is not None:
                self.problem.code = edited_code
                self._update_code_preview()
                self.app.notify("Code updated", severity="information")
        except Exception as e:
            self.app.notify_error(f"Failed to open editor: {str(e)}")
    
    def action_save_changes(self) -> None:
        """Save changes to the problem."""
        if not self.problem:
            return
        
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
        
        try:
            # Save to database
            self.db.update_problem(self.problem)
            self.app.notify_success(f"Problem '{title}' updated successfully!")
            
            # Go back to previous screen
            self.app.pop_screen()
            
        except Exception as e:
            self.app.notify_error(f"Failed to save changes: {str(e)}")
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        # Check if there are unsaved changes
        if self._has_unsaved_changes():
            self.app.notify_warning("Unsaved changes will be lost. Press Esc again to confirm.")
            # TODO: Add proper confirmation dialog
        
        self.app.pop_screen()
    
    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        if not self.problem or not self.original_problem:
            return False
        
        title = self.query_one("#title_input", Input).value.strip()
        link = self.query_one("#link_input", Input).value.strip()
        
        return (
            title != self.original_problem.title or
            link != self.original_problem.link or
            self.problem.approach != self.original_problem.approach or
            self.problem.code != self.original_problem.code
        )
    
    def refresh_data(self) -> None:
        """Refresh screen data."""
        if self.problem:
            # Reload problem from database to get latest data
            updated_problem = self.db.get_problem(self.problem.id)
            if updated_problem:
                self.set_problem(updated_problem)