from PIL import Image
import os
import sys
import PyPDF2
import curses


def extract_metadata(file_path):
    if file_path.endswith(".pdf"):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        with Image.open(file_path) as img:
            metadata = img.info
    else:
        print("Unsupported file type")
        sys.exit(1)

    return {key: metadata[key] for key in metadata}


def save_metadata(file_path, metadata):
    if file_path.endswith(".pdf"):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.add_metadata(metadata)

            with open(file_path, 'wb') as output_file:
                writer.write(output_file)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        with Image.open(file_path) as img:
            img.save(file_path, **metadata)
    else:
        print("Unsupported file type")
        sys.exit(1)


def main(stdscr, file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    metadata = extract_metadata(file_path)
    quitting_menu = False
    quit_key = ""
    editing = False
    cursor_line = 0
    cursor_position = 0

    curses.curs_set(0)  # Hide the cursor

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Display metadata
        keys = list(metadata.keys())
        if not keys:
            stdscr.addstr(0, 0, "No metadata available")
        else:
            for idx, key in enumerate(keys):
                value = metadata[key]
                if isinstance(value, str):
                    display_text = f"{key}: {value}"
                else:
                    display_text = f"{key}: {str(value)}"
                stdscr.addstr(idx, 0, display_text)

        if quitting_menu:
            # Display "Quit menu" in the footer
            stdscr.addstr(height - 1, 0, f"Quit menu {quit_key}", curses.A_REVERSE)
        elif editing:
            # Display "Editing" in the footer
            stdscr.addstr(height - 1, 0, "Editing", curses.A_REVERSE)

        # Draw the cursor
        if editing and keys:
            stdscr.addstr(cursor_line, cursor_position, " ", curses.A_REVERSE)

        stdscr.refresh()

        ch = stdscr.getch()

        # Quit menu
        if ch == 27:  # 27 is the ASCII code for the "Esc" key
            quitting_menu = True
        elif quitting_menu:
            if ch == 127:  # Backspace key
                if quit_key:
                    quit_key = quit_key[:-1]
            elif ch == 10 or ch == 13:  # Enter key
                if quit_key == ":x" or quit_key == ":q!":
                    break
                else:
                    quitting_menu = False
                    quit_key = ""
            elif ch < 256:
                quit_key += chr(ch)

        # Editing mode
        elif ch == 14:  # Ctrl + n
            editing = not editing
            if editing and keys:
                cursor_position = len(keys[0]) + 2
            else:
                cursor_position = 0

        elif editing and keys:
            key = keys[cursor_line]
            value = metadata[key]
            max_cursor_position = len(key) + 2 + len(str(value))

            if ch == curses.KEY_DOWN and cursor_line < len(keys) - 1:
                cursor_line += 1
                value = metadata[keys[cursor_line]]
                if isinstance(value, str):
                    cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(value))
                else:
                    cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(str(value)))
            elif ch == curses.KEY_UP and cursor_line > 0:
                cursor_line -= 1
                value = metadata[keys[cursor_line]]
                if isinstance(value, str):
                    cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(value))
                else:
                    cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(str(value)))
            elif ch == curses.KEY_LEFT and cursor_position > len(key) + 2:
                cursor_position -= 1
            elif ch == curses.KEY_RIGHT and cursor_position < max_cursor_position:
                cursor_position += 1
            elif ch == 127:  # Backspace key
                if cursor_position > len(key) + 2:
                    if isinstance(value, str):
                        metadata[key] = value[:cursor_position - len(key) - 3] + value[cursor_position - len(key) - 2:]
                    else:
                        metadata[key] = str(value)[:cursor_position - len(key) - 3] + str(value)[cursor_position - len(key) - 2:]
                    cursor_position = max(cursor_position - 1, len(key) + 2)
            elif ch == 330:  # Delete key
                if cursor_position < max_cursor_position:
                    if isinstance(value, str):
                        metadata[key] = value[:cursor_position - len(key) - 2] + value[cursor_position - len(key) - 1:]
                    else:
                        metadata[key] = str(value)[:cursor_position - len(key) - 2] + str(value)[cursor_position - len(key) - 1:]
            elif ch < 256:
                if isinstance(value, str):
                    metadata[key] = value[:cursor_position - len(key) - 2] + chr(ch) + value[cursor_position - len(key) - 2:]
                else:
                    metadata[key] = str(value)[:cursor_position - len(key) - 2] + chr(ch) + str(value)[cursor_position - len(key) - 2:]
                cursor_position += 1

    stdscr.clear()
    stdscr.refresh()

    if quit_key == ":x":
        save_metadata(file_path, metadata)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    curses.wrapper(main, file_path)
