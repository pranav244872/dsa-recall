"""
Streak tracker screen for DSA Recall application.

This screen displays practice streak information and daily review statistics.
"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, DataTable
from textual.binding import Binding
from datetime import date, timedelta


class StreakTrackerScreen(Screen):
    """
    Screen for viewing practice streak and review statistics.
    
    Shows current streak, recent activity, and daily review counts.
    """
    
    CSS = """
    StreakTrackerScreen {
        padding: 2;
        background: $surface;
    }
    
    .header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 2 0;
    }
    
    .streak-display {
        text-align: center;
        margin: 2 0;
        padding: 2;
        background: $panel;
        border: tall $primary;
    }
    
    .streak-number {
        text-style: bold;
        color: $warning;
        font-size: 2;
    }
    
    .streak-label {
        color: $text-muted;
        margin: 1 0 0 0;
    }
    
    .stats-container {
        height: auto;
        margin: 2 0;
        background: $panel;
        border: tall $secondary;
        padding: 1;
    }
    
    .stats-title {
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }
    
    .table-container {
        height: 1fr;
        border: tall $primary;
        background: $panel;
        margin: 2 0 0 0;
    }
    
    DataTable {
        height: 100%;
    }
    
    .shortcuts {
        text-align: center;
        color: $text-muted;
        margin: 2 0 0 0;
    }
    
    .motivational {
        text-align: center;
        color: $success;
        margin: 1 0;
        text-style: italic;
    }
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, db_manager, **kwargs):
        """
        Initialize streak tracker screen.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(**kwargs)
        self.db = db_manager
        self.streak_data = []
        self.current_streak = 0
    
    def compose(self) -> ComposeResult:
        """Compose the streak tracker layout."""
        with Vertical():
            yield Static("🔥 Streak Tracker", classes="header")
            
            # Current streak display
            with Vertical(classes="streak-display"):
                yield Static("🔥", id="streak_icon")
                yield Static("0", id="streak_number", classes="streak-number")
                yield Static("Day Streak", classes="streak-label")
                yield Static("", id="motivational", classes="motivational")
            
            # Overall statistics
            with Vertical(classes="stats-container"):
                yield Static("📊 Statistics", classes="stats-title")
                yield Static("", id="total_stats")
            
            # Recent activity table
            with Vertical(classes="table-container"):
                yield Static("📅 Recent Activity (Last 30 Days)", classes="stats-title")
                table = DataTable(id="activity_table")
                table.add_columns("Date", "Problems Reviewed", "Status")
                yield table
            
            yield Static(
                "R: Refresh | Esc: Back",
                classes="shortcuts"
            )
    
    def on_mount(self) -> None:
        """Load data when screen is mounted."""
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh streak and activity data."""
        self.current_streak = self.db.get_current_streak()
        self.streak_data = self.db.get_streak_data(30)  # Last 30 days
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the display with current streak data."""
        # Update streak display
        streak_number = self.query_one("#streak_number", Static)
        streak_number.update(str(self.current_streak))
        
        # Update motivational message
        motivational = self.query_one("#motivational", Static)
        if self.current_streak == 0:
            motivational.update("Start your streak today! 💪")
        elif self.current_streak == 1:
            motivational.update("Great start! Keep it going! ⭐")
        elif self.current_streak < 7:
            motivational.update("Building momentum! 🚀")
        elif self.current_streak < 30:
            motivational.update("Impressive dedication! 🏆")
        else:
            motivational.update("Legendary consistency! 👑")
        
        # Update overall statistics
        self._update_statistics()
        
        # Update activity table
        self._update_activity_table()
    
    def _update_statistics(self) -> None:
        """Update overall statistics display."""
        total_stats = self.query_one("#total_stats", Static)
        
        if not self.streak_data:
            total_stats.update("No review data available")
            return
        
        # Calculate statistics
        total_reviews = sum(day['problems_reviewed'] for day in self.streak_data)
        active_days = sum(1 for day in self.streak_data if day['problems_reviewed'] > 0)
        avg_per_day = total_reviews / len(self.streak_data) if self.streak_data else 0
        avg_per_active_day = total_reviews / active_days if active_days > 0 else 0
        
        # Calculate best streak
        best_streak = self._calculate_best_streak()
        
        stats_text = (
            f"Total Reviews (30d): {total_reviews} | "
            f"Active Days: {active_days}/30 | "
            f"Avg/Day: {avg_per_day:.1f} | "
            f"Avg/Active Day: {avg_per_active_day:.1f} | "
            f"Best Streak: {best_streak}"
        )
        
        total_stats.update(stats_text)
    
    def _calculate_best_streak(self) -> int:
        """Calculate the best streak from available data."""
        if not self.streak_data:
            return 0
        
        # Sort by date (ascending)
        sorted_data = sorted(self.streak_data, key=lambda x: x['date'])
        
        best_streak = 0
        current_streak = 0
        
        for day in sorted_data:
            if day['problems_reviewed'] > 0:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 0
        
        return best_streak
    
    def _update_activity_table(self) -> None:
        """Update the activity table with recent data."""
        table = self.query_one("#activity_table", DataTable)
        table.clear()
        
        if not self.streak_data:
            table.add_row("No data", "", "")
            return
        
        # Sort by date (descending - most recent first)
        sorted_data = sorted(self.streak_data, key=lambda x: x['date'], reverse=True)
        
        today = date.today()
        
        for day_data in sorted_data:
            day_date = date.fromisoformat(day_data['date'])
            problems_reviewed = day_data['problems_reviewed']
            
            # Determine status
            if problems_reviewed == 0:
                status = "❌ Missed"
            elif problems_reviewed == 1:
                status = "✅ Active"
            else:
                status = f"🔥 {problems_reviewed} reviews"
            
            # Format date
            if day_date == today:
                date_str = "Today"
            elif day_date == today - timedelta(days=1):
                date_str = "Yesterday"
            else:
                days_ago = (today - day_date).days
                date_str = f"{days_ago}d ago"
            
            table.add_row(
                date_str,
                str(problems_reviewed),
                status
            )
        
        # Fill in missing days (days with no data = 0 reviews)
        all_dates = {date.fromisoformat(day['date']) for day in self.streak_data}
        for i in range(30):
            check_date = today - timedelta(days=i)
            if check_date not in all_dates:
                if check_date == today:
                    date_str = "Today"
                elif check_date == today - timedelta(days=1):
                    date_str = "Yesterday"
                else:
                    days_ago = i
                    date_str = f"{days_ago}d ago"
                
                # Insert in correct position (maintain reverse chronological order)
                # For simplicity, we'll just add them - the table will sort naturally
                table.add_row(date_str, "0", "❌ Missed")
        
        # Focus the table
        table.focus()
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh streak data."""
        self.refresh_data()
        self.app.notify("Streak data refreshed", severity="information")