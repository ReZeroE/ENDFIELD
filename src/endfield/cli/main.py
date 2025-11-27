from datetime import datetime

from rich.table import Table
from tabulate import tabulate
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Static,
    ListView,
    ListItem,
    Label,
    Input,
    TabbedContent,
    TabPane,
    RichLog,
    DataTable,
    Tree,
    MarkdownViewer,
)

from test import SystemMonitor
from constants import (
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_TRANSPARENT,
    COLOR_PRIMARY_BLUE,
    COLOR_FOCUS_YELLOW,
    COLOR_PURPLE_ACCENT,
    COLOR_PINK_ACCENT,
    COLOR_TEXT_GRAY,
    COLOR_TEXT_DIM,
    COLOR_TEXT_DISABLED,
    COLOR_STATUS_GREEN,
    COLOR_BG_DARK_SLATE,
    COLOR_BG_DARKER,
    COLOR_BG_SLATE,
    COLOR_RED
)


# Organized actions by module
ACTION_MODULES = {
    "☆ Start/Stop": [
        ("start_game", "▶  Start game"),
        ("stop_game", "■  Stop game"),
    ],
    "☆ Scheduler": [
        ("schedule_start", "⏰ Schedule start"),
        ("schedule_stop", "⏰ Schedule stop"),
    ],
    "☆ Quick Directory Access": [
        ("open_logs_dir", "📂 Open logs directory"),
        ("open_screenshots_dir", "🖼  Open screenshots directory"),
    ],
    "☆ Other": [
        ("show_status", "ℹ  Show current game status"),
    ],
    "☆ Settings": [
        ("dev_switch", "🐛 Toggle Dev Mode"),
    ],
    "☆ Miscellaneous": [],
}

# Organized links by category
LINK_CATEGORIES = {
    "Official Resources": [
        ("open_website", "🌐 Official website"),
        ("open_docs", "📄 Documentation"),
        ("open_changelog", "📋 Changelog"),
    ],
    "Community": [
        ("open_forum", "💬 User forum"),
        ("open_discord", "💭 Discord server"),
        ("open_reddit", "🔴 Reddit community"),
    ],
    "Support & Help": [
        ("open_support", "🆘 Contact support"),
        ("open_faq", "❓ FAQ page"),
        ("open_tutorials", "📚 Tutorials"),
        ("open_troubleshooting", "🔧 Troubleshooting guide"),
    ],
}

COMMANDS = [
    'help',
    'start-game',
    'stop-game',
    'status',
    'clear',
    'dev'
]


class EndfieldCLI(App):
    """ENDFIELD CLI dashboard with RichLog + DataTable status tabs + toast + action disabling."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "cursor_down_actions"),
        ("k", "cursor_up_actions"),
        ("enter", "select_action", "Select"),
        ("C", "clear_logs", "Clear logs"),        # SHIFT + C
        ("R", "refresh_status", "Refresh status"), # SHIFT + R
        ("tab", "focus_next", "Next panel"),
        ("shift+tab", "focus_previous", "Previous panel")
    ]

    CSS = f"""
    Screen {{
        layout: vertical;
        background: {COLOR_BLACK};
        color: {COLOR_TEXT_GRAY};
        padding: 0 1 0 1;
    }}

    #header {{
        height: auto;
        background: {COLOR_BLACK};
        color: {COLOR_WHITE};
        padding: 1 1 0 1;
        margin-bottom: 1;
    }}

    #main {{
        layout: horizontal;
        height: 1fr;
    }}

    #left-column {{
        layout: vertical;
        width: 2fr;
        height: 1fr;
    }}

    #right-column {{
        layout: vertical;
        width: 5fr;
        height: 1fr;
    }}

    #top-row {{
        layout: horizontal;
        height: 1fr;
        margin-bottom: 1;
    }}

    /* Game status tabbed area + logs tabbed area */
    #status-tabbed {{
        border: round {COLOR_PRIMARY_BLUE};
        padding: 1;
        height: 1fr;
        width: 1fr;
        margin-right: 1;
        background: {COLOR_BLACK};
        color: {COLOR_STATUS_GREEN};
    }}

    #status-tabbed:focus-within {{
        border: heavy {COLOR_FOCUS_YELLOW};
    }}

    #logs-tabbed {{
        border: round {COLOR_PRIMARY_BLUE};
        padding: 1;
        height: 1fr;
        width: 1fr;
        margin-left: 1;
        background: {COLOR_BLACK};
    }}

    #logs-tabbed:focus-within {{
        border: heavy {COLOR_FOCUS_YELLOW};
    }}

    #logs-log, #logs-other-log {{
        background: {COLOR_BLACK};
    }}

    #config-log {{
        background: {COLOR_BLACK};
    }}

    /* Quick Actions sidebar */
    #quick-actions-tabbed {{
        border: round {COLOR_PRIMARY_BLUE};
        padding: 1;
        height: 1fr;
        margin-right: 1;
        background: {COLOR_BLACK};
    }}

    #quick-actions-tabbed:focus-within {{
        border: heavy {COLOR_FOCUS_YELLOW};
    }}

    /* CLI area */
    #cli-area {{
        layout: vertical;
        height: 1fr;
    }}

    #cli-tabbed {{
        border: round {COLOR_PRIMARY_BLUE};
        padding: 1;
        height: 1fr;
        background: {COLOR_BLACK};
    }}

    #cli-tabbed:focus-within {{
        border: heavy {COLOR_FOCUS_YELLOW};
    }}

    /* DataTable styling */
    DataTable {{
        background: {COLOR_BLACK};
        height: 1fr;
    }}
    
    DataTable > .datatable--header {{
        background: {COLOR_BG_DARK_SLATE};
        color: {COLOR_TEXT_DIM};
    }}
    
    DataTable > .datatable--cursor {{
        background: {COLOR_TRANSPARENT};
    }}

    /* MarkdownViewer styling */
    MarkdownViewer {{
        background: {COLOR_BLACK};
        height: 1fr;
    }}

    /* Tree widget styling */
    Tree {{
        background: {COLOR_BLACK};
        height: 1fr;
    }}

    Tree > .tree--label {{
        background: {COLOR_TRANSPARENT};
    }}

    Tree > .tree--guides {{
        color: {COLOR_BG_SLATE};
    }}

    Tree > .tree--cursor {{
        background: {COLOR_BG_DARK_SLATE};
    }}

    Tree > .tree--highlight {{
        background: {COLOR_BG_DARK_SLATE};
    }}

    #actions-list {{
        height: 1fr;
        overflow-y: auto;
    }}

    #links-list {{
        height: 1fr;
        overflow-y: auto;
    }}

    ListView > ListItem.section-header {{
        padding: 1 1;
        margin-top: 1;
        background: {COLOR_TRANSPARENT};
        color: {COLOR_PRIMARY_BLUE};
    }}

    ListView > ListItem.section-header:hover {{
        background: {COLOR_TRANSPARENT};
    }}

    ListView > ListItem.section-header.--highlight {{
        background: {COLOR_TRANSPARENT};
        color: {COLOR_PRIMARY_BLUE};
        text-style: none;
    }}

    ListView > ListItem {{
        padding: 0 1;
    }}

    ListView > ListItem.--highlight {{
        background: {COLOR_BG_DARK_SLATE};
        color: {COLOR_FOCUS_YELLOW};
        text-style: bold;
    }}

    /* Disabled actions: gray text, even when highlighted */
    ListView > ListItem.disabled {{
        color: {COLOR_TEXT_DISABLED};
    }}

    ListView > ListItem.disabled.--highlight {{
        background: {COLOR_BG_DARKER};
        color: {COLOR_TEXT_DISABLED};
        text-style: none;
    }}

    /* Terminal pane styling */
    #terminal-pane {{
        layout: vertical;
        height: 1fr;
    }}

    #terminal-log {{
        background: {COLOR_BLACK};
        border: none;
        overflow-y: auto;
        height: 1fr;
        margin-bottom: 0;
        padding: 1 1 0 1;
    }}

    #terminal-input-container {{
        layout: horizontal;
        height: auto;
        background: {COLOR_BLACK};
        padding: 0 0 0 1;
        margin: 0;
        border: round {COLOR_BG_DARK_SLATE};
    }}

    #terminal-prompt {{
        background: {COLOR_BLACK};
        color: {COLOR_PRIMARY_BLUE};
        width: auto;
        height: 1;
        padding: 0 1 0 0;
        margin: 0;
    }}

    #terminal-input {{
        background: {COLOR_BLACK};
        border: none;
        padding: 0;
        height: 1;
        color: {COLOR_WHITE};
        width: 1fr;
        margin: 0;
    }}

    #terminal-input:focus {{
        background: {COLOR_BLACK};
        border: none;
    }}

    #terminal-input > .input--cursor {{
        background: {COLOR_PRIMARY_BLUE};
        color: {COLOR_BLACK};
    }}

    #terminal-info-icon {{
        background: {COLOR_BLACK};
        color: {COLOR_PRIMARY_BLUE};
        width: auto;
        height: 1;
        margin: 0 1 0 0;
    }}

    #terminal-info-icon:hover {{
        color: {COLOR_FOCUS_YELLOW};
        text-style: bold;
        margin: 0 1 0 0;
    }}

    #footer {{
        height: auto;
        background: {COLOR_BLACK};
        color: {COLOR_TEXT_GRAY};
        padding: 0 1 0 1;
    }}
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Track which actions are disabled (by action_id)
        self.disabled_actions: set[str] = set()
        # Terminal command history
        self.terminal_history: list[str] = []
        self.history_index: int = -1
        # System monitor for host info
        self.system_monitor = SystemMonitor()
        # Track if host info tab is active
        self.host_info_tab_active: bool = False
        # Dev mode flag
        self.dev_mode: bool = False

    # ---------- Layout ----------

    def compose(self) -> ComposeResult:
        # Header - custom static with left and right aligned text
        yield Static(id="header")

        with Horizontal(id="main"):
            # Left column: Quick Actions
            with Vertical(id="left-column"):
                with TabbedContent(id="quick-actions-tabbed"):
                    # Actions tab with Tree widget
                    with TabPane("Actions", id="actions-pane"):
                        yield Tree("Actions", id="actions-tree")

                    # Quick links tab
                    with TabPane("Links", id="links-pane"):
                        yield ListView(
                            # Official Resources section
                            ListItem(Label("[bold cyan]━━━ Official Resources ━━━[/bold cyan]"), disabled=True, classes="section-header"),
                            *[
                                ListItem(Label(label), id=link_id)
                                for link_id, label in LINK_CATEGORIES["Official Resources"]
                            ],
                            # Community section
                            ListItem(Label("[bold cyan]━━━ Community ━━━[/bold cyan]"), disabled=True, classes="section-header"),
                            *[
                                ListItem(Label(label), id=link_id)
                                for link_id, label in LINK_CATEGORIES["Community"]
                            ],
                            # Support & Help section
                            ListItem(Label("[bold cyan]━━━ Support & Help ━━━[/bold cyan]"), disabled=True, classes="section-header"),
                            *[
                                ListItem(Label(label), id=link_id)
                                for link_id, label in LINK_CATEGORIES["Support & Help"]
                            ],
                            id="links-list",
                        )

            # Right column: Game Status + CLI Control (top) and CLI (bottom)
            with Vertical(id="right-column"):
                # Top row: game status (tabbed) + CLI Control (logs)
                with Horizontal(id="top-row"):
                    # Game Status: TabbedContent with 3 tabs
                    with TabbedContent(id="status-tabbed"):
                        with TabPane("Live Game Status", id="live-pane"):
                            yield DataTable(id="status-live", show_header=False, cursor_type="none")
                        with TabPane("Host Info", id="host-pane"):
                            yield DataTable(id="status-host", show_header=False, cursor_type="none")

                    # CLI Control: TabbedContent with Logs + Configuration
                    with TabbedContent(id="logs-tabbed"):
                        with TabPane("Logs", id="logs-pane"):
                            yield RichLog(id="logs-log", markup=True, highlight=False)
                        with TabPane("Configuration", id="config-pane"):
                            yield RichLog(id="config-log", markup=True, highlight=False)

                # Bottom: CLI area
                with Vertical(id="cli-area"):
                    with TabbedContent(id="cli-tabbed"):
                        with TabPane("Terminal", id="terminal-pane"):
                            yield RichLog(id="terminal-log", markup=True, highlight=False)
                            with Horizontal(id="terminal-input-container"):
                                yield Static(">", id="terminal-prompt")
                                yield Input(
                                    placeholder="start-game",
                                    id="terminal-input",
                                )
                                yield Static("ⓘ", id="terminal-info-icon")
                        with TabPane("Game Info", id="game-pane"):
                            yield MarkdownViewer(id="status-game", show_table_of_contents=False)
                        with TabPane("Help", id="help-pane"):
                            yield MarkdownViewer(id="help-viewer", show_table_of_contents=False)

        # Footer
        yield Static(id="footer")

    # ---------- Widget helpers ----------

    @property
    def host_status_table(self) -> DataTable:
        return self.query_one("#status-host", DataTable)

    @property
    def game_info_viewer(self) -> MarkdownViewer:
        return self.query_one("#status-game", MarkdownViewer)

    @property
    def live_status_table(self) -> DataTable:
        return self.query_one("#status-live", DataTable)

    @property
    def logs_panel(self) -> RichLog:
        # main Logs tab log
        return self.query_one("#logs-log", RichLog)

    @property
    def config_log(self) -> RichLog:
        # Configuration tab log
        return self.query_one("#config-log", RichLog)

    @property
    def other_logs_panel(self) -> RichLog:
        # "Other" log tab, in case you want to log something else later
        return self.query_one("#logs-other-log", RichLog)

    @property
    def actions_tree(self) -> Tree:
        return self.query_one("#actions-tree", Tree)

    @property
    def links_list(self) -> ListView:
        return self.query_one("#links-list", ListView)

    @property
    def terminal_log(self) -> RichLog:
        return self.query_one("#terminal-log", RichLog)

    @property
    def terminal_input(self) -> Input:
        return self.query_one("#terminal-input", Input)

    @property
    def help_viewer(self) -> MarkdownViewer:
        return self.query_one("#help-viewer", MarkdownViewer)

    # ---------- Initialization ----------

    def on_mount(self) -> None:
        # Populate header with title and author
        header = self.query_one("#header", Static)
        header_table = Table.grid(expand=True)
        header_table.add_column(justify="left")
        header_table.add_column(justify="right")
        
        # Build title with dev mode indicator
        title_left = f"[bold {COLOR_PURPLE_ACCENT}]ARKNIGHTS:ENDFIELD CLI[/bold {COLOR_PURPLE_ACCENT}] [dim]v1.0.0[/dim]"
        if self.dev_mode:
            title_left += f" [white][[/white][{COLOR_RED}]DEV MODE[/{COLOR_RED}][white]][/white]"
        
        header_table.add_row(
            title_left,
            "[dim]Developed by Kevin L.[/dim]"
        )
        header.update(header_table)

        # Populate footer with navigation instructions
        footer = self.query_one("#footer", Static)
        footer_table = Table.grid(expand=True)
        footer_table.add_column(justify="center")
        footer_table.add_row(
            "[dim]Tab[/dim] change panel  •  [dim]j/k[/dim] or [dim]arrow keys[/dim] navigate up and down  •  [dim]ctrl+q[/dim] to quit"
        )
        footer.update(footer_table)

        # Border titles
        quick_actions_tabbed = self.query_one("#quick-actions-tabbed", TabbedContent)
        quick_actions_tabbed.border_title = "Quick Actions"
        quick_actions_tabbed.can_focus = False  # Prevent TabbedContent from being focused

        status_tabbed = self.query_one("#status-tabbed", TabbedContent)
        status_tabbed.border_title = "Game Status"
        status_tabbed.border_subtitle = f"[{COLOR_PURPLE_ACCENT}][SHIFT+R] REFRESH[/{COLOR_PURPLE_ACCENT}]"
        status_tabbed.can_focus = False

        logs_tabbed = self.query_one("#logs-tabbed", TabbedContent)
        logs_tabbed.border_title = "CLI Control"
        logs_tabbed.border_subtitle = f"[{COLOR_PURPLE_ACCENT}][SHIFT+C] CLEAR[/{COLOR_PURPLE_ACCENT}]"
        logs_tabbed.can_focus = False

        cli_tabbed = self.query_one("#cli-tabbed", TabbedContent)
        cli_tabbed.border_title = "Interactive Terminal"
        cli_tabbed.can_focus = False  # Prevent TabbedContent from being focused

        # Set initial datetime subtitle on CLI border (bottom right)
        cli_tabbed.border_subtitle = self._formatted_now()

        # Update the datetime every 10 seconds
        self.set_interval(10, self._update_cli_datetime)

        # Initialize actions tree
        self._init_actions_tree()

        # Focus Quick Actions panel by default
        quick_actions_tabbed.focus()

        # Initialize DataTables
        self._init_status_tables()

        # Initialize Help content
        self._init_help_content()

        # Show welcome message in terminal
        self._terminal_write("[bold cyan]ENDFIELD CLI Interactive Terminal[/bold cyan]", system=False)
        self._terminal_write("[dim] - Type 'help' to see available commands[/dim]", system=False)
        self._terminal_write("")  # Empty line
        
        # Focus the actions tree by default (left panel)
        self.call_after_refresh(lambda: self.actions_tree.focus())
        
        # Start updating host info every 3 seconds
        self.set_interval(3, self._update_host_info_table)
        
        # Initialize configuration display
        self._refresh_config_display()

    def _refresh_config_display(self) -> None:
        """Refresh the configuration display with current settings."""
        self.config_log.clear()
        
        # Create settings table using tabulate
        settings_data = [
            ["Dev Mode", "[green]ON[/green]" if self.dev_mode else "[red]OFF[/red]"],
        ]
        
        table = tabulate(settings_data, headers=["Setting", "Value"], tablefmt="simple")
        
        self.config_log.write("[bold cyan]Application Settings[/bold cyan]")
        self.config_log.write("")
        self.config_log.write(table)
        self.config_log.write("")
        self.config_log.write("[dim]Use Quick Actions > Settings to toggle settings[/dim]")
        self.config_log.write("[dim]Or use 'dev' command in terminal[/dim]")

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab activation events."""
        if event.pane.id == "terminal-pane":
            # Focus the terminal input
            self.call_after_refresh(self._focus_terminal_input)
            
        if event.pane.id == "links-pane":
            # Auto-select first item in links list for j/k navigation
            self.call_after_refresh(self._focus_links_list)
        
        # Track Host Info tab activation for lazy loading
        if event.pane.id == "host-pane":
            self.host_info_tab_active = True
            # Immediately update when tab is activated
            self._update_host_info_table()
        elif event.tabbed_content.id == "status-tabbed":
            # If switching away from host pane within status-tabbed
            self.host_info_tab_active = False
    
    def on_focus(self, event) -> None:
        """Auto-focus terminal input when terminal-related widgets get focus."""
        if hasattr(event.widget, 'id'):
            widget_id = event.widget.id
            
            # Focus input when cli-tabbed gets focus and Terminal tab is active
            if widget_id == "cli-tabbed":
                try:
                    cli_tabbed = self.query_one("#cli-tabbed", TabbedContent)
                    if cli_tabbed.active == "terminal-pane":
                        self.call_after_refresh(self._focus_terminal_input)
                except Exception:
                    pass
            
            # Focus input when terminal pane is focused
            elif widget_id == "terminal-pane":
                self.call_after_refresh(self._focus_terminal_input)
            
            # Focus input when terminal log (RichLog content) is focused
            elif widget_id == "terminal-log":
                self.call_after_refresh(self._focus_terminal_input)
    
    def on_blur(self, event) -> None:
        """Handle blur events to clear tree selection when Quick Actions loses focus."""
        # Check if the quick actions tree is losing focus
        if hasattr(event.widget, 'id') and event.widget.id == "actions-tree":
            # Clear the cursor selection
            try:
                tree = self.actions_tree
                # Move cursor to no selection
                if tree.cursor_node:
                    tree.cursor_node = None
            except Exception:
                pass
    
    def _focus_terminal_input(self) -> None:
        """Focus the terminal input field."""
        try:
            self.terminal_input.focus()
        except Exception:
            pass
    
    def _focus_links_list(self) -> None:
        """Focus the links list and select first non-header item."""
        try:
            links_list = self.links_list
            links_list.focus()
            # Select the first non-header item (skip section headers)
            if len(links_list) > 0:
                # First item is a header, so select second item (first actual link)
                if len(links_list) > 1:
                    links_list.index = 1
        except Exception:
            pass  # Widget might not be ready yet
    
    def _check_initial_focus(self) -> None:
        """Check if Terminal tab is active on startup and focus input."""
        try:
            cli_tabbed = self.query_one("#cli-tabbed", TabbedContent)
            if cli_tabbed.active == "terminal-pane":
                self.terminal_input.focus()
        except Exception:
            pass

    # ---------- Status table initialization ----------

    def _init_actions_tree(self) -> None:
        """Initialize the actions tree with modules and actions."""
        tree = self.actions_tree
        tree.clear()
        tree.show_root = False
        tree.guide_depth = 2
        
        # Add each module and its actions
        for module_name, actions in ACTION_MODULES.items():
            module_node = tree.root.add(f"[bold cyan]{module_name}[/bold cyan]", expand=False)
            module_node.data = {"type": "module", "name": module_name}
            
            for action_id, action_label in actions:
                action_node = module_node.add(action_label)
                action_node.data = {"type": "action", "id": action_id, "label": action_label}

    def _init_status_tables(self) -> None:
        """Initialize all status DataTables with columns and initial data."""
        # Live Game Status
        self.live_status_table.add_columns("Property", "Value")
        self.live_status_table.add_rows([
            ("Status", "[dim]Not started[/dim]"),
            ("Started On", "[dim]N/A[/dim]"),
            ("CPU", "[dim]N/A[/dim]"),
            ("GPU", "[dim]N/A[/dim]"),
            ("Memory", "[dim]N/A[/dim]"),
            ("Uptime", "[dim]N/A[/dim]"),
        ])

        # Game Info
        game_info_markdown = r"""
| Property | Value |
|----------|-------|
| Game     | ENDFIELD |
| Version  | dev |
| Engine   | Unity |
| Path  | D:\Workspace\Endfield\Workspace\Endfield\test.txt |
"""
        self.game_info_viewer.document.update(game_info_markdown)

        # Host Info - Initialize with system information
        self._init_host_info_table()

    def _init_host_info_table(self) -> None:
        """Initialize the Host Info table with system information."""
        info = self.system_monitor.get_all_info()
        self.host_status_table.add_columns("Property", "Value")
        self.host_status_table.add_rows([
            ("Host", info["host"]),
            ("OS", info["os"]),
            ("Arch", info["arch"]),
            ("CPU", f"[cyan]{info['cpu']}[/cyan]"),
            ("GPU", f"[magenta]{info['gpu']}[/magenta]"),
            ("RAM", f"[yellow]{info['ram']}[/yellow]"),
        ])
    
    def _update_host_info_table(self) -> None:
        """Update the dynamic parts of the Host Info table (CPU, GPU, RAM) - only when tab is active."""
        # Only update if the Host Info tab is currently active
        if not self.host_info_tab_active:
            return
        
        info = self.system_monitor.get_all_info()
        self.host_status_table.clear()
        self.host_status_table.add_rows([
            ("Host", info["host"]),
            ("OS", info["os"]),
            ("Arch", info["arch"]),
            ("CPU", f"[cyan]{info['cpu']}[/cyan]"),
            ("GPU", f"[magenta]{info['gpu']}[/magenta]"),
            ("RAM", f"[yellow]{info['ram']}[/yellow]"),
        ])
        
        # Log the system info update
        self._log(f"[dim]System info updated.[/dim]", dev_only=True)

    def _init_help_content(self) -> None:
        """Initialize the Help tab content."""
        help_markdown = """
# ENDFIELD CLI Help

## Available Commands

### Terminal Commands
- `help` - Show available commands
- `start-game` - Start the game
- `stop-game` - Stop the game
- `status` - Show current game status
- `clear` - Clear the terminal
- `dev` - Toggle dev mode on/off

## Keyboard Shortcuts

### Navigation
- `j` - Move cursor down in Actions tree
- `k` - Move cursor up in Actions tree
- `Enter` - Select action or toggle module
- `q` - Quit application

### Terminal
- Click on the Terminal tab or press Tab to navigate to it
- Type commands directly in the terminal (no input box needed)
- `↑` (Up Arrow) - Navigate backward in command history
- `↓` (Down Arrow) - Navigate forward in command history
- `Backspace` - Delete last character
- `Enter` - Execute command

### Panel Actions
- `SHIFT+C` - Clear logs panel
- `SHIFT+R` - Refresh game status

## Quick Actions

Use the Actions tree in the left panel to:
- Start/Stop the game
- Schedule start/stop times
- Open logs and screenshots directories
- Check game status

## Links

Quick access to:
- Official website
- User forum
- Support
- FAQ
- Tutorials
"""
        self.help_viewer.document.update(help_markdown)

    def _update_live_status_table(self, data: dict[str, str]) -> None:
        """Update the Live Game Status table with new data."""
        self.live_status_table.clear()
        rows = [
            ("Status", data.get("status", "[dim]N/A[/dim]")),
            ("Started On", data.get("started_on", "[dim]N/A[/dim]")),
            ("CPU", data.get("cpu", "[dim]N/A[/dim]")),
            ("GPU", data.get("gpu", "[dim]N/A[/dim]")),
            ("Memory", data.get("memory", "[dim]N/A[/dim]")),
            ("Uptime", data.get("uptime", "[dim]N/A[/dim]")),
        ]
        self.live_status_table.add_rows(rows)

    # ---------- Date/time helpers ----------

    def _formatted_now(self) -> str:
        """Return current date/time in 'Nov.15 2024 13:03' format."""
        now = datetime.now()
        return f"[{COLOR_PINK_ACCENT}]{now.strftime('%b.%d %Y %H:%M')}[/{COLOR_PINK_ACCENT}]"

    def _update_cli_datetime(self) -> None:
        """Refresh the bottom-right subtitle on the CLI border."""
        # Keep the SHIFT+T clear terminal instruction
        # (removed datetime update as it would conflict with the clear instruction)

    def _update_header(self) -> None:
        """Update the header to reflect current dev mode status."""
        header = self.query_one("#header", Static)
        header_table = Table.grid(expand=True)
        header_table.add_column(justify="left")
        header_table.add_column(justify="right")
        
        # Build title with dev mode indicator
        title_left = f"[bold {COLOR_PURPLE_ACCENT}]ARKNIGHTS:ENDFIELD CLI[/bold {COLOR_PURPLE_ACCENT}] [dim]v1.0.0[/dim]"
        if self.dev_mode:
            title_left += f" [white][[/white][{COLOR_RED}]DEV MODE[/{COLOR_RED}][white]][/white]"
        
        header_table.add_row(
            title_left,
            "[dim]Developed by Kevin L.[/dim]"
        )
        header.update(header_table)

    # ---------- Public toast method ----------

    class ToastSeverity:
        INFORMATION = "information"
        WARNING = "warning"
        ERROR = "error"
        SUCCESS = "success"

    def show_toast(
        self,
        message: str,
        title: str = "",
        severity: str = "information",
        timeout: float = 1.5,
    ) -> None:
        """
        Show a notification toast with severity styling.
        """
        self.notify(message=message, title=title, severity=severity, timeout=timeout)

    # ---------- Public action-enable API ----------

    def set_action_enabled(self, action_id: str, enabled: bool) -> None:
        """
        Enable or disable an action by its action_id.

        When disabled:
        - The item stays visible but is styled gray.
        - Selecting it will do nothing except log a note.
        """
        if enabled:
            self.disabled_actions.discard(action_id)
        else:
            self.disabled_actions.add(action_id)

        # Update the ListItem style if it's present
        self._update_action_item_style(action_id)

    def _update_action_item_style(self, action_id: str) -> None:
        """Apply or remove the 'disabled' CSS class on tree nodes."""
        if not self.is_running:
            return

        # Update tree nodes
        tree = self.actions_tree
        for module_node in tree.root.children:
            for action_node in module_node.children:
                if action_node.data and action_node.data.get("id") == action_id:
                    is_disabled = action_id in self.disabled_actions
                    if is_disabled:
                        # Make the label gray
                        original_label = action_node.data.get("label", "")
                        action_node.label = f"[dim]{original_label}[/dim]"
                    else:
                        # Restore original label
                        action_node.label = action_node.data.get("label", "")
                    break

    # ---------- Vim-style navigation for Actions ----------

    def action_cursor_down_actions(self) -> None:
        # Work for actions tree
        if self.actions_tree.has_focus:
            self.actions_tree.action_cursor_down()
        # Work for any focused ListView in links
        else:
            try:
                focused = self.focused
                if isinstance(focused, ListView):
                    focused.action_cursor_down()
            except Exception:
                pass

    def action_cursor_up_actions(self) -> None:
        # Work for actions tree
        if self.actions_tree.has_focus:
            self.actions_tree.action_cursor_up()
        # Work for any focused ListView in links
        else:
            try:
                focused = self.focused
                if isinstance(focused, ListView):
                    focused.action_cursor_up()
            except Exception:
                pass

    def action_select_action(self) -> None:
        """Handle Enter key on tree - toggle modules or execute actions."""
        tree = self.actions_tree
        
        # Handle tree selection if tree has focus
        if tree.has_focus and tree.cursor_node is not None:
            node_data = tree.cursor_node.data
            if not node_data:
                return
                
            if node_data.get("type") == "module":
                # Toggle module expansion
                tree.cursor_node.toggle()
            elif node_data.get("type") == "action":
                # Execute the action
                action_id = node_data.get("id")
                if action_id:
                    self._run_action(action_id)
        # Handle ListView selection if a ListView has focus
        else:
            try:
                focused = self.focused
                if isinstance(focused, ListView):
                    focused.action_select()
            except Exception:
                pass

    # ---------- Tree selection ----------

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection (click or Enter)."""
        node_data = event.node.data
        if not node_data:
            return
            
        if node_data.get("type") == "action":
            action_id = node_data.get("id")
            if action_id:
                self._run_action(action_id)

    # ---------- Actions list selection ----------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        action_id = event.item.id
        # Don't execute if it's a section header (no id or None)
        if action_id:
            self._run_action(action_id)

    # ---------- CLI input handling ----------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle terminal command submission."""
        if event.input.id == "terminal-input":
            cmd = event.value.strip()
            
            if not cmd:
                return

            # Display the command that was entered
            self._terminal_write(f"[{COLOR_PRIMARY_BLUE}]>[/{COLOR_PRIMARY_BLUE}] {cmd}", system=False)

            # Add to history
            self.terminal_history.append(cmd)
            self.history_index = len(self.terminal_history)

            # Execute command
            self._execute_terminal_command(cmd)

            # Clear input
            event.input.value = ""

    def on_click(self, event) -> None:
        """Handle clicks on terminal area and info icon."""
        if hasattr(event.widget, 'id'):
            widget_id = event.widget.id
            
            # Show tooltip when clicking on info icon
            if widget_id == "terminal-info-icon":
                self.show_toast(
                    "1. Use ↑/↓ for history.\n2. Type 'help' for available commands.\n3. Unix terminal keybindings supported.",
                    title="Terminal Help",
                    severity=self.ToastSeverity.INFORMATION,
                    timeout=4.0
                )
            
            # Focus input when clicking on terminal log
            elif widget_id == "terminal-log":
                self._focus_terminal_input()
            
            # Focus input when clicking on terminal pane
            elif widget_id == "terminal-pane":
                self._focus_terminal_input()

    def on_key(self, event) -> None:
        """Handle up/down arrows for command history in terminal."""
        terminal_input = self.terminal_input
        
        # Only handle if terminal input is focused
        if not terminal_input.has_focus:
            return
            
        if event.key == "up":
            if self.terminal_history and self.history_index > 0:
                self.history_index -= 1
                terminal_input.value = self.terminal_history[self.history_index]
                terminal_input.cursor_position = len(terminal_input.value)
                event.prevent_default()
        elif event.key == "down":
            if self.terminal_history:
                if self.history_index < len(self.terminal_history) - 1:
                    self.history_index += 1
                    terminal_input.value = self.terminal_history[self.history_index]
                    terminal_input.cursor_position = len(terminal_input.value)
                else:
                    self.history_index = len(self.terminal_history)
                    terminal_input.value = ""
                event.prevent_default()

    # ---------- CLEAR logs action (SHIFT + C) ----------

    def action_clear_logs(self) -> None:
        """Clear the main logs panel via SHIFT+C."""
        self.logs_panel.clear()
        self.show_toast("Logs cleared", severity=self.ToastSeverity.INFORMATION)
        self._log("[blue]Logs cleared (hotkey)[/blue]")

    # ---------- REFRESH status action (SHIFT + R) ----------

    def action_refresh_status(self) -> None:
        """Refresh the live game status via SHIFT+R (same as show_status stub)."""
        self._set_live_status({
            "status": "[green]Running[/green]",
            "started_on": "2025-11-25 10:30",
            "cpu": "[cyan]45%[/cyan]",
            "gpu": "[magenta]78%[/magenta]",
            "memory": "[yellow]2.3 GB[/yellow]",
            "uptime": "2h 15m",
        })
        self._log("[blue]Status refreshed (hotkey)[/blue]")

    # ---------- Helpers ----------

    def _log(self, msg: str, dev_only: bool = False) -> None:
        """Write markup-capable text to the main Logs RichLog.
        
        Args:
            msg: The message to log
            dev_only: If True, only log when dev_mode is enabled
        """
        # Only log dev-only messages if dev mode is on
        if dev_only and not self.dev_mode:
            return
        self.logs_panel.write(f"[[{COLOR_PURPLE_ACCENT}]EF[/{COLOR_PURPLE_ACCENT}]] {msg}")

    def _terminal_write(self, msg: str, system: bool = True) -> None:
        """Write markup-capable text to the terminal RichLog."""
        prefix = ''
        if (msg and system):
            prefix = f"[[{COLOR_PURPLE_ACCENT}]EF[/{COLOR_PURPLE_ACCENT}]] "
        self.terminal_log.write(f"{prefix}{msg}")

    def _set_live_status(self, data: dict[str, str]) -> None:
        """Convenience: update the Live Game Status tab with new data."""
        self._update_live_status_table(data)

    def _execute_terminal_command(self, cmd: str) -> None:
        """Execute a terminal command and display output."""
        # Parse command (simple space split for now)
        parts = cmd.split()
        if not parts:
            return

        command = parts[0].lower()

        # Check if command is supported
        if command not in COMMANDS:
            self._terminal_write(f"[red]Error:[/red] Unknown command '{command}' [dim]Type 'help' to see available commands[/dim]")
            return

        # Execute the command
        if command == "help":
            self._terminal_write("[bold]Available commands:[/bold]")
            self._terminal_write("  [cyan]help[/cyan]        - Show this help message")
            self._terminal_write("  [cyan]start-game[/cyan]  - Start the game")
            self._terminal_write("  [cyan]stop-game[/cyan]   - Stop the game")
            self._terminal_write("  [cyan]status[/cyan]      - Show current game status")
            self._terminal_write("  [cyan]dev[/cyan]         - Toggle dev mode")
            self._terminal_write("  [cyan]clear[/cyan]       - Clear terminal")

        elif command == "dev":
            self.dev_mode = not self.dev_mode
            status = "enabled" if self.dev_mode else "disabled"
            self._terminal_write(f"[cyan]Dev mode {status}[/cyan]")
            self.show_toast(f"Dev mode {status}", severity=self.ToastSeverity.INFORMATION)
            self._refresh_config_display()
            # Update header to show/hide dev mode indicator
            self._update_header()

        elif command == "start-game":
            self._terminal_write("[green]Starting game...[/green]")
            self._set_live_status({
                "status": "[yellow]Starting...[/yellow]",
                "started_on": "[dim]N/A[/dim]",
                "cpu": "[dim]N/A[/dim]",
                "gpu": "[dim]N/A[/dim]",
                "memory": "[dim]N/A[/dim]",
                "uptime": "[dim]N/A[/dim]",
            })
            self._log("[green]Game start triggered via terminal[/green]")

        elif command == "stop-game":
            self._terminal_write("[yellow]Stopping game...[/yellow]")
            self._set_live_status({
                "status": "[red]Stopping...[/red]",
                "started_on": "[dim]N/A[/dim]",
                "cpu": "[dim]N/A[/dim]",
                "gpu": "[dim]N/A[/dim]",
                "memory": "[dim]N/A[/dim]",
                "uptime": "[dim]N/A[/dim]",
            })
            self._log("[yellow]Game stop triggered via terminal[/yellow]")

        elif command == "status":
            self._terminal_write("[bold]Current Game Status:[/bold]")
            self._set_live_status({
                "status": "[green]Running[/green]",
                "started_on": "2025-11-25 10:30",
                "cpu": "[cyan]45%[/cyan]",
                "gpu": "[magenta]78%[/magenta]",
                "memory": "[yellow]2.3 GB[/yellow]",
                "uptime": "2h 15m",
            })
            self._terminal_write("  Status: [green]Running[/green]")
            self._terminal_write("  Started: 2025-11-25 10:30")
            self._terminal_write("  CPU: [cyan]45%[/cyan]")
            self._terminal_write("  GPU: [magenta]78%[/magenta]")
            self._terminal_write("  Memory: [yellow]2.3 GB[/yellow]")
            self._terminal_write("  Uptime: 2h 15m")
            self._log("[blue]Status refreshed via terminal[/blue]")

        elif command == "clear":
            self.terminal_log.clear()
            self._terminal_write("[dim]Terminal cleared[/dim]")

    def _run_action(self, action_id: str) -> None:
        # If disabled, show a small note and bail
        if action_id in self.disabled_actions:
            self._log(f"[dim]>>> {action_id} (disabled)[/dim]")
            return

        self._log(f"[dim]>>> {action_id}[/dim]")

        if action_id == "start_game":
            self._set_live_status({
                "status": "[yellow]Starting...[/yellow]",
                "started_on": "[dim]N/A[/dim]",
                "cpu": "[dim]N/A[/dim]",
                "gpu": "[dim]N/A[/dim]",
                "memory": "[dim]N/A[/dim]",
                "uptime": "[dim]N/A[/dim]",
            })
            self._log("[green]Start triggered[/green]")

        elif action_id == "stop_game":
            self._set_live_status({
                "status": "[red]Stopping...[/red]",
                "started_on": "[dim]N/A[/dim]",
                "cpu": "[dim]N/A[/dim]",
                "gpu": "[dim]N/A[/dim]",
                "memory": "[dim]N/A[/dim]",
                "uptime": "[dim]N/A[/dim]",
            })
            self._log("[yellow]Stop triggered[/yellow]")

        elif action_id == "open_logs_dir":
            self._log("📂 Would open logs directory (stub).")

        elif action_id == "open_screenshots_dir":
            self._log("🖼  Would open screenshots directory (stub).")

        elif action_id == "show_status":
            self._set_live_status({
                "status": "[green]Running[/green]",
                "started_on": "2025-11-25 10:30",
                "cpu": "[cyan]45%[/cyan]",
                "gpu": "[magenta]78%[/magenta]",
                "memory": "[yellow]2.3 GB[/yellow]",
                "uptime": "2h 15m",
            })
            self._log("[blue]Status refreshed[/blue]")

        elif action_id == "schedule_start":
            self._log("⏰ Would open scheduling UI for start (stub).")
            self.show_toast("Scheduled start (stub)")

        elif action_id == "schedule_stop":
            self._log("⏰ Would open scheduling UI for stop (stub).")
            self.show_toast("Scheduled stop (stub)", severity=self.ToastSeverity.WARNING)

        elif action_id == "dev_switch":
            self.dev_mode = not self.dev_mode
            status = "enabled" if self.dev_mode else "disabled"
            self.show_toast(f"Dev mode {status}", severity=self.ToastSeverity.INFORMATION)
            self._refresh_config_display()
            # Update header to show/hide dev mode indicator
            self._update_header()

        else:
            self._log("[red]Not implemented yet[/red]")


if __name__ == "__main__":
    print("Starting ENDFIELD CLI...")
    
    app = EndfieldCLI()

    # Example: start with "show_status" disabled
    def disable_after_mount() -> None:
        app.set_action_enabled("show_status", False)

    app.call_after_refresh(disable_after_mount)
    app.run()
