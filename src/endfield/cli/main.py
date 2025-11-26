from datetime import datetime

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


ASCII_TITLE = r"""
███████╗███╗   ██╗██████╗ ███████╗██╗███████╗██╗     ██████╗      ██████╗██╗     ██╗
██╔════╝████╗  ██║██╔══██╗██╔════╝██║██╔════╝██║     ██╔══██╗    ██╔════╝██║     ██║
█████╗  ██╔██╗ ██║██║  ██║█████╗  ██║█████╗  ██║     ██║  ██║    ██║     ██║     ██║
██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██║██╔══╝  ██║     ██║  ██║    ██║     ██║     ██║
███████╗██║ ╚████║██████╔╝██║     ██║███████╗███████╗██████╔╝    ╚██████╗███████╗██║
╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝╚══════╝╚═╝
"""

SUBTITLE = "[grey58]Developed by Kevin L.[/grey58]"

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
    'clear'
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

    CSS = """
    Screen {
        layout: vertical;
        background: black;
        color: #7d807d; /* text color for the developed by text */
        padding: 1 2;
    }

    #title {
        text-align: center;
        color: #bd81e6; /* title ascii art */
        height: auto;
    }

    #subtitle {
        text-align: center;
        height: auto;
        margin-bottom: 1;
    }

    #main {
        layout: horizontal;
        height: 1fr;
    }

    #left-column {
        layout: vertical;
        width: 2fr;
        height: 1fr;
    }

    #right-column {
        layout: vertical;
        width: 5fr;
        height: 1fr;
    }

    #top-row {
        layout: horizontal;
        height: 1fr;
        margin-bottom: 1;
    }

    /* Game status tabbed area + logs tabbed area */
    #status-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        width: 1fr;
        margin-right: 1;
        background: black;
        color: #bbf7d0;
    }

    #status-tabbed:focus-within {
        border: heavy #facc15;
    }

    #logs-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        width: 1fr;
        margin-left: 1;
        background: black;
    }

    #logs-tabbed:focus-within {
        border: heavy #facc15;
    }

    #logs-log, #logs-other-log {
        background: black;
    }

    /* Quick Actions sidebar */
    #quick-actions-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        margin-right: 1;
        background: black;
    }

    #quick-actions-tabbed:focus-within {
        border: heavy #facc15;
    }

    /* CLI area */
    #cli-area {
        layout: vertical;
        height: 1fr;
    }

    #cli-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        background: black;
    }

    #cli-tabbed:focus-within {
        border: heavy #facc15;
    }

    /* DataTable styling */
    DataTable {
        background: black;
        height: 1fr;
    }
    
    DataTable > .datatable--header {
        background: #1e293b;
        color: #94a3b8;
    }
    
    DataTable > .datatable--cursor {
        background: transparent;
    }

    /* MarkdownViewer styling */
    MarkdownViewer {
        background: black;
        height: 1fr;
    }

    /* Tree widget styling */
    Tree {
        background: black;
        height: 1fr;
    }

    Tree > .tree--label {
        background: transparent;
    }

    Tree > .tree--guides {
        color: #475569;
    }

    Tree > .tree--cursor {
        background: #1e293b;
    }

    Tree > .tree--highlight {
        background: #1e293b;
    }

    #actions-list {
        height: 1fr;
        overflow-y: auto;
    }

    #links-list {
        height: 1fr;
        overflow-y: auto;
    }

    ListView > ListItem.section-header {
        padding: 1 1;
        margin-top: 1;
        background: transparent;
        color: #54acff;
    }

    ListView > ListItem.section-header:hover {
        background: transparent;
    }

    ListView > ListItem.section-header.--highlight {
        background: transparent;
        color: #54acff;
        text-style: none;
    }

    ListView > ListItem {
        padding: 0 1;
    }

    ListView > ListItem.--highlight {
        background: #1e293b;
        color: #facc15;
        text-style: bold;
    }

    /* Disabled actions: gray text, even when highlighted */
    ListView > ListItem.disabled {
        color: #6b7280;
    }

    ListView > ListItem.disabled.--highlight {
        background: #111827;
        color: #6b7280;
        text-style: none;
    }

    /* Terminal pane styling */
    #terminal-pane {
        layout: vertical;
        height: 1fr;
    }

    #terminal-log {
        background: black;
        border: none;
        overflow-y: auto;
        height: 1fr;
        margin-bottom: 1;
    }

    #terminal-input {
        background: black;
        border: heavy #64748b;
        padding: 0 1;
        height: auto;
        color: white;
    }

    #terminal-input:focus {
        border: heavy #64748b;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Track which actions are disabled (by action_id)
        self.disabled_actions: set[str] = set()
        # Terminal command history
        self.terminal_history: list[str] = []
        self.history_index: int = -1

    # ---------- Layout ----------

    def compose(self) -> ComposeResult:
        # Header
        yield Static(ASCII_TITLE.strip("\n"), id="title")
        yield Static(SUBTITLE, id="subtitle")

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
                        with TabPane("Game Info", id="game-pane"):
                            yield MarkdownViewer(id="status-game", show_table_of_contents=False)
                        with TabPane("Host Info", id="host-pane"):
                            yield DataTable(id="status-host", show_header=False, cursor_type="none")

                    # CLI Control: TabbedContent with Logs + Configuration
                    with TabbedContent(id="logs-tabbed"):
                        with TabPane("Logs", id="logs-pane"):
                            yield RichLog(id="logs-log", markup=True, highlight=False)
                        with TabPane("Configuration", id="logs-other-pane"):
                            yield RichLog(
                                id="logs-other-log",
                                markup=True,
                                highlight=False,
                            )

                # Bottom: CLI area
                with Vertical(id="cli-area"):
                    with TabbedContent(id="cli-tabbed"):
                        with TabPane("Terminal", id="terminal-pane"):
                            yield RichLog(id="terminal-log", markup=True, highlight=False)
                            yield Input(
                                placeholder="Type a command...",
                                id="terminal-input",
                            )
                        with TabPane("Help", id="help-pane"):
                            yield MarkdownViewer(id="help-viewer", show_table_of_contents=False)

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
        # Border titles
        quick_actions_tabbed = self.query_one("#quick-actions-tabbed", TabbedContent)
        quick_actions_tabbed.border_title = "Quick Actions"
        quick_actions_tabbed.can_focus = False  # Prevent TabbedContent from being focused

        status_tabbed = self.query_one("#status-tabbed", TabbedContent)
        status_tabbed.border_title = "Game Status"
        status_tabbed.border_subtitle = "[#bd81e6][SHIFT+R] REFRESH[/#bd81e6]"
        status_tabbed.can_focus = False

        logs_tabbed = self.query_one("#logs-tabbed", TabbedContent)
        logs_tabbed.border_title = "CLI Control"
        logs_tabbed.border_subtitle = "[#bd81e6][SHIFT+C] CLEAR[/#bd81e6]"
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
        self._terminal_write("[bold cyan]ENDFIELD Terminal[/bold cyan]")
        self._terminal_write("[dim]Type 'help' to see available commands[/dim]")
        
        # Focus the actions tree by default (left panel)
        self.call_after_refresh(lambda: self.actions_tree.focus())

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Auto-focus terminal input when Terminal tab is activated."""
        if event.pane.id == "terminal-pane":
            # Use call_after_refresh to ensure the widget is ready
            self.call_after_refresh(self._focus_terminal_input)
        elif event.pane.id == "links-pane":
            # Auto-select first item in links list for j/k navigation
            self.call_after_refresh(self._focus_links_list)
    
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
            pass  # Widget might not be ready yet
    
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
        game_info_markdown = """
| Property | Value |
|----------|-------|
| Game     | ENDFIELD |
| Version  | dev |
| Engine   | Unity |
| Path  | D:\Workspace\Endfield\\Workspace\Endfield\\test.txt |
"""
        self.game_info_viewer.document.update(game_info_markdown)

        # Host Info
        self.host_status_table.add_columns("Property", "Value")
        self.host_status_table.add_rows([
            ("Host", "[dim]unknown[/dim]"),
            ("OS", "[dim]unknown[/dim]"),
        ])

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

## Keyboard Shortcuts

### Navigation
- `j` - Move cursor down in Actions tree
- `k` - Move cursor up in Actions tree
- `Enter` - Select action or toggle module
- `q` - Quit application

### Terminal
- `↑` (Up Arrow) - Navigate backward in command history
- `↓` (Down Arrow) - Navigate forward in command history

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
        return f"[#cf5990]{now.strftime('%b.%d %Y %H:%M')}[/#cf5990]"

    def _update_cli_datetime(self) -> None:
        """Refresh the bottom-right subtitle on the CLI border."""
        # Keep the SHIFT+T clear terminal instruction
        # (removed datetime update as it would conflict with the clear instruction)

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
        if event.input.id == "terminal-input":
            cmd = event.value.strip()
            
            if not cmd:
                # Just clear and return for empty command
                event.input.value = ""
                return

            # Add to history
            self.terminal_history.append(cmd)
            self.history_index = len(self.terminal_history)

            # Display command in terminal with prompt
            self._terminal_write(f"[#54acff]$[/#54acff] {cmd}")

            # Execute command (will write output and new prompt)
            self._execute_terminal_command(cmd)

            # Clear input
            event.input.value = ""

    def on_key(self, event) -> None:
        """Handle up/down arrows for command history in terminal and tab navigation."""
        # Handle tab and shift+tab for panel navigation only
        if event.key == "tab":
            self.action_focus_next()
            event.prevent_default()
            event.stop()
            return
        elif event.key == "shift+tab":
            self.action_focus_previous()
            event.prevent_default()
            event.stop()
            return
        
        # Handle terminal history navigation
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

    def _log(self, msg: str) -> None:
        """Write markup-capable text to the main Logs RichLog."""
        self.logs_panel.write(f"[[#bd81e6]EF[/#bd81e6]] {msg}")

    def _terminal_write(self, msg: str) -> None:
        """Write markup-capable text to the terminal RichLog."""
        self.terminal_log.write(msg)

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
            self._terminal_write(f"[red]Error:[/red] Unknown command '{command}'")
            self._terminal_write(f"[dim]Type 'help' to see available commands[/dim]")
            return

        # Execute the command
        if command == "help":
            self._terminal_write("[bold]Available commands:[/bold]")
            self._terminal_write("  [cyan]help[/cyan]        - Show this help message")
            self._terminal_write("  [cyan]start-game[/cyan]  - Start the game")
            self._terminal_write("  [cyan]stop-game[/cyan]   - Stop the game")
            self._terminal_write("  [cyan]status[/cyan]      - Show current game status")

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

        else:
            self._log("[red]Not implemented yet[/red]")


if __name__ == "__main__":
    app = EndfieldCLI()

    # Example: start with "show_status" disabled
    def disable_after_mount() -> None:
        app.set_action_enabled("show_status", False)

    app.call_after_refresh(disable_after_mount)
    app.run()
