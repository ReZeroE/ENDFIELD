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

QUICK_LINKS = [
    ("open_website", "🌐 Open official website"),
    ("open_forum", "💬 Open user forum"),
    ("open_support", "🆘 Contact support"),
    ("open_faq", "❓ Open FAQ page"),
    ("open_tutorials", "📚 Open tutorials"),
]

COMMANDS = [
    'help',
    'start-game',
    'stop-game',
    'status'
]


class EndfieldCLI(App):
    """ENDFIELD CLI dashboard with RichLog + DataTable status tabs + toast + action disabling."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "cursor_down_actions"),
        ("k", "cursor_up_actions"),
        ("enter", "select_action", "Select"),
        ("C", "clear_logs", "Clear logs"),        # SHIFT + C
        ("R", "refresh_status", "Refresh status") # SHIFT + R
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
        height: 3fr;
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

    #logs-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        width: 1fr;
        margin-left: 1;
        background: black;
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

    /* CLI area */
    #cli-area {
        layout: vertical;
        height: 2fr;
    }

    #cli-tabbed {
        border: round #54acff;
        padding: 1;
        height: 1fr;
        background: black;
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

    #cli-pane {
        layout: vertical;
    }

    #cli-help {
        color: #94a3b8;
        margin-bottom: 1;
    }

    #cli-input {
        border: heavy #64748b;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Track which actions are disabled (by action_id)
        self.disabled_actions: set[str] = set()

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
                            *[
                                ListItem(Label(label), id=a_id)
                                for a_id, label in QUICK_LINKS
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
                        with TabPane("CLI", id="cli-pane"):
                            yield Static(
                                "Type a command and press Enter:",
                                id="cli-help",
                            )
                            yield Input(
                                placeholder="start-game",
                                id="cli-input",
                            )

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

    # ---------- Initialization ----------

    def on_mount(self) -> None:
        # Border titles
        self.query_one("#quick-actions-tabbed", TabbedContent).border_title = "Quick Actions"

        status_tabbed = self.query_one("#status-tabbed", TabbedContent)
        status_tabbed.border_title = "Game Status"
        status_tabbed.border_subtitle = "[#bd81e6][SHIFT+R] REFRESH[/#bd81e6]"

        logs_tabbed = self.query_one("#logs-tabbed", TabbedContent)
        logs_tabbed.border_title = "CLI Control"
        logs_tabbed.border_subtitle = "[#bd81e6][SHIFT+C] CLEAR[/#bd81e6]"

        cli_tabbed = self.query_one("#cli-tabbed", TabbedContent)
        cli_tabbed.border_title = "CLI"

        # Set initial datetime subtitle on CLI border (bottom right)
        cli_tabbed.border_subtitle = self._formatted_now()

        # Update the datetime every 10 seconds
        self.set_interval(10, self._update_cli_datetime)

        # Initialize actions tree
        self._init_actions_tree()

        # Focus actions tree by default
        self.actions_tree.focus()

        # Initialize DataTables
        self._init_status_tables()

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
        cli_tabbed = self.query_one("#cli-tabbed", TabbedContent)
        cli_tabbed.border_subtitle = self._formatted_now()

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
        self.actions_tree.action_cursor_down()

    def action_cursor_up_actions(self) -> None:
        self.actions_tree.action_cursor_up()

    def action_select_action(self) -> None:
        """Handle Enter key on tree - toggle modules or execute actions."""
        tree = self.actions_tree
        if tree.cursor_node is None:
            return
            
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
        self._run_action(action_id)

    # ---------- CLI input handling ----------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "cli-input":
            return

        cmd = event.value.strip()
        if not cmd:
            return

        # RichLog supports markup
        self._log(f"[cyan]$ {cmd}[/cyan]")
        self._log("[dim](CLI command execution not implemented yet)[/dim]")

        event.input.value = ""

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

    def _set_live_status(self, data: dict[str, str]) -> None:
        """Convenience: update the Live Game Status tab with new data."""
        self._update_live_status_table(data)

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
