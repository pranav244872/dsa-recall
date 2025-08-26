"""
Collapsible text widget for the DSA Recall TUI.

This widget allows showing/hiding long text content with a toggle mechanism.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static, Button
from textual.binding import Binding
from textual.reactive import reactive


class CollapsibleText(Widget):
    """
    A widget that can show/hide text content with a toggle button.
    
    Useful for showing long text like problem approaches and code
    that should be hidden by default to keep the UI clean.
    """
    
    DEFAULT_CSS = """
    CollapsibleText {
        height: auto;
        margin: 1 0;
    }
    
    CollapsibleText .header {
        background: $surface;
        padding: 0 1;
        height: 1;
    }
    
    CollapsibleText .content {
        padding: 0 2;
        background: $surface-lighten-1;
        border-left: thick $accent;
    }
    
    CollapsibleText .content-hidden {
        display: none;
    }
    """
    
    BINDINGS = [
        Binding("enter", "toggle", "Toggle"),
    ]
    
    expanded = reactive(False)
    
    def __init__(
        self,
        title: str,
        content: str,
        shortcut_key: str = None,
        expanded: bool = False,
        **kwargs
    ):
        """
        Initialize collapsible text widget.
        
        Args:
            title: Header title for the collapsible section
            content: Text content to show/hide
            shortcut_key: Keyboard shortcut for toggling (e.g. 'a', 'c')
            expanded: Whether to start expanded
        """
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.shortcut_key = shortcut_key
        self.expanded = expanded
        
        if shortcut_key:
            # Add dynamic binding for the shortcut key
            self._bindings.bind(shortcut_key, "toggle", f"Toggle {title}")
    
    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        # Create header with toggle indicator
        indicator = "▼" if self.expanded else "▶"
        shortcut_text = f"[{self.shortcut_key}]" if self.shortcut_key else ""
        header_text = f"{indicator} {shortcut_text} {self.title}"
        
        with Vertical():
            yield Static(header_text, classes="header", id="header")
            if self.expanded and self.content.strip():
                yield Static(self.content, classes="content", id="content")
    
    def action_toggle(self) -> None:
        """Toggle the expanded state."""
        self.expanded = not self.expanded
        self.refresh()
    
    def watch_expanded(self, expanded: bool) -> None:
        """React to expanded state changes."""
        self.refresh()
    
    def set_content(self, content: str) -> None:
        """Update the content text."""
        self.content = content
        self.refresh()
    
    def set_title(self, title: str) -> None:
        """Update the title text."""
        self.title = title
        self.refresh()
    
    def refresh(self) -> None:
        """Refresh the widget display."""
        # Update header
        indicator = "▼" if self.expanded else "▶"
        shortcut_text = f"[{self.shortcut_key}]" if self.shortcut_key else ""
        header_text = f"{indicator} {shortcut_text} {self.title}"
        
        header = self.query_one("#header", Static)
        header.update(header_text)
        
        # Show/hide content
        try:
            content_widget = self.query_one("#content", Static)
            if self.expanded and self.content.strip():
                content_widget.display = True
                content_widget.update(self.content)
            else:
                content_widget.display = False
        except:
            # Content widget doesn't exist yet, will be created in compose
            if self.expanded and self.content.strip():
                # Remove existing content and add new one
                self.recompose()


class ProblemDetails(Widget):
    """
    Widget for displaying problem details with collapsible sections.
    
    Shows problem title, link, and collapsible approach/code sections.
    """
    
    DEFAULT_CSS = """
    ProblemDetails {
        height: auto;
        padding: 1;
        background: $panel;
        border: tall $primary;
    }
    
    ProblemDetails .title {
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }
    
    ProblemDetails .link {
        color: $warning;
        margin: 0 0 1 0;
    }
    
    ProblemDetails .shortcuts {
        margin: 1 0 0 0;
        color: $text-muted;
    }
    """
    
    def __init__(self, problem=None, **kwargs):
        """
        Initialize problem details widget.
        
        Args:
            problem: Problem instance to display
        """
        super().__init__(**kwargs)
        self.problem = problem
    
    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        if not self.problem:
            yield Static("No problem selected", classes="title")
            return
        
        with Vertical():
            # Title and link
            yield Static(f"📌 Title: {self.problem.title}", classes="title")
            if self.problem.link:
                yield Static(f"🔗 Link: {self.problem.link}", classes="link")
            
            # Collapsible approach
            if self.problem.approach:
                yield CollapsibleText(
                    title="Approach",
                    content=self.problem.approach,
                    shortcut_key="a",
                    expanded=False
                )
            
            # Collapsible code
            if self.problem.code:
                yield CollapsibleText(
                    title="Code",
                    content=self.problem.code,
                    shortcut_key="c",
                    expanded=False
                )
            
            # Shortcuts help
            shortcuts_text = (
                "[a] Toggle Approach | [c] Toggle Code | "
                "[e] Mark Easy | [h] Mark Hard | [←] Back"
            )
            yield Static(shortcuts_text, classes="shortcuts")
    
    def update_problem(self, problem):
        """Update the displayed problem."""
        self.problem = problem
        self.recompose()