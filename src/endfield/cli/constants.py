

# ============================================================================
# ENDFIELD CLI - Color Constants
# ============================================================================
# This file contains all color hex values used throughout the CLI application.
# Modify these values to easily customize the color scheme without editing CSS.
# ============================================================================

# ----------------------------------------------------------------------------
# Base Colors
# ----------------------------------------------------------------------------
COLOR_BLACK = "black"                # Main background color
COLOR_WHITE = "white"                # Primary text color (headers, input text)
COLOR_TRANSPARENT = "transparent"    # Transparent backgrounds (labels, cursors)

# ----------------------------------------------------------------------------
# Primary UI Accent Colors
# ----------------------------------------------------------------------------
COLOR_PRIMARY_BLUE = "#54acff"       # Main accent color used for:
                                      # - Panel borders (default state)
                                      # - Terminal prompt
                                      # - Info icon
                                      # - Section headers in lists
                                      # - Terminal command prefix

COLOR_FOCUS_YELLOW = "#facc15"       # Focus/highlight color used for:
                                      # - Panel borders when focused
                                      # - Highlighted list items
                                      # - Hover states

COLOR_PURPLE_ACCENT = "#bd81e6"      # Branding/title color used for:
                                      # - Application title
                                      # - Border subtitles (SHIFT+R, SHIFT+C)
                                      # - Log prefixes ([EF])

COLOR_PINK_ACCENT = "#cf5990"        # Date/time display color

# ----------------------------------------------------------------------------
# Text Colors
# ----------------------------------------------------------------------------
COLOR_TEXT_GRAY = "#7d807d"          # Default secondary text color
COLOR_TEXT_DIM = "#94a3b8"           # Dimmed text (table headers)
COLOR_TEXT_DISABLED = "#6b7280"      # Disabled action items
COLOR_STATUS_GREEN = "#bbf7d0"       # Status panel text color

# ----------------------------------------------------------------------------
# Background Colors (Semantic)
# ----------------------------------------------------------------------------
COLOR_BG_DARK_SLATE = "#1e293b"      # Used for:
                                      # - DataTable headers
                                      # - Tree cursor/highlight
                                      # - List item highlights
                                      # - Terminal input container border

COLOR_BG_DARKER = "#111827"          # Darker background for disabled highlighted items

COLOR_BG_SLATE = "#475569"           # Tree guide lines color

COLOR_RED = "#e85454"