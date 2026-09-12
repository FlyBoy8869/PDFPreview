from enum import IntEnum, StrEnum


class Icons(StrEnum):
    ACROBAT_LOGO = "acrobat_logo.png"
    COLLAPSE = "collapse.png"
    COPY_TO_CLIPBOARD = "copy_to_clipboard.png"
    DUPLICATE = "duplicate.png"
    EXPLORER = "explorer.png"
    FOLDER = "folder.png"
    HIDE_FILES = "hide_files.png"
    MOVE = "move.png"
    NEW_TEXT = "new_text_file.webp"
    OPEN_WITH = "open_with.png"
    PALETTE = "palette.png"
    PLUS = "plus.png"
    RENAME = "rename.png"
    SHOW_FILES = "show_files.png"
    TRASHCAN = "trashcan.png"


class Indent(IntEnum):
    INDENT_MIN = 5
    INDENT_MAX = 50
    INDENT_DEFAULT = 20
    INDENT_STEP = 1
    INDENT_TICK_INTERVAL = 5
    INDENT_TOOL_WIDTH = 100


class FileViewMode(StrEnum):
    HIDE = "hide"
    SHOW = "show"
