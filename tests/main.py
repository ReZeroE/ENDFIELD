from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.widgets import Frame, Box, TextArea, RadioList, Label
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition

# =========================
# ASCII header
# =========================
ASCII_TITLE = r"""
   ____        _   _           _       
  |  _ \ _   _| |_| |__   ___ | |_ ___ 
  | |_) | | | | __| '_ \ / _ \| __/ __|
  |  __/| |_| | |_| | | | (_) | |_\__ \
  |_|    \__, |\__|_| |_|\___/ \__|___/
         |___/                         
"""

# =========================
# Shared widgets
# =========================

status_panel = TextArea(
    text="CPU: 17%\nMemory: 42%\nJobs: 0\nStatus: Idle\n",
    read_only=True,
)

log_panel = TextArea(
    text="Logs:\nApp started.\n",
    read_only=True,
    scrollbar=True,
)

# Actions menu: (label, internal value)
actions_menu = RadioList(
    [
        ("Run main job", "run_job"),
        ("Open details screen", "details"),
        ("Quit application", "quit"),
    ]
)

# =========================
# Screen 1: Main dashboard
# =========================

main_screen_container = HSplit(
    [
        Label(ASCII_TITLE, style="class:ascii-title"),
        VSplit(
            [
                Frame(status_panel, title="Status"),
                Frame(log_panel, title="Logs"),
            ],
            padding=1,
        ),
        Frame(actions_menu, title="Actions (↑/↓ to move, Enter to select)"),
    ],
    padding=1,
)

# =========================
# Screen 2: Details view
# =========================

details_text = TextArea(
    text=(
        "Details Screen\n\n"
        "Here you can show more info,\n"
        "settings, etc.\n\n"
        "Press 'b' to go back."
    ),
    read_only=True,
)

details_screen_container = HSplit(
    [
        Label(ASCII_TITLE, style="class:ascii-title"),
        Frame(details_text, title="Details"),
        Box(Label("Press 'b' to go back to main menu"), height=1),
    ],
    padding=1,
)

# Start with main screen, and explicitly focus the actions menu
layout = Layout(main_screen_container, focused_element=actions_menu)

# =========================
# Key bindings
# =========================

kb = KeyBindings()

# Only grab Enter when the actions_menu has focus.
# `eager=True` makes this run before the widget's own Enter handler.
@kb.add(
    "enter",
    filter=Condition(lambda: layout.has_focus(actions_menu)),
    eager=True,
)
def _(event):
    """
    Execute the currently selected action from the actions_menu.
    """
    current = actions_menu.current_value  # "run_job", "details", or "quit"

    if current == "run_job":
        log_panel.buffer.insert_text("Running main job...\nDone.\n")

    elif current == "details":
        # Switch to details screen
        layout.container = details_screen_container
        event.app.invalidate()

    elif current == "quit":
        event.app.exit()


@kb.add("b")
def _(event):
    """
    Go back to main screen (from details).
    """
    layout.container = main_screen_container
    # Make sure focus goes back to the actions menu so arrows & Enter work.
    layout.focus(actions_menu)
    event.app.invalidate()


@kb.add("q")
def _(event):
    """
    Quit from anywhere.
    """
    event.app.exit()


# =========================
# Styling
# =========================

style = Style.from_dict(
    {
        "frame.label": "bold",
        "ascii-title": "bold ansimagenta",
        "radio.focused": "reverse",
        "radio.selected": "bold",
    }
)

# =========================
# Build app
# =========================

app = Application(
    layout=layout,
    key_bindings=kb,
    style=style,
    full_screen=True,
)


def main():
    app.run()


if __name__ == "__main__":
    main()
