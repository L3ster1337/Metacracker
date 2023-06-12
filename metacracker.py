import os
import sys
import PyPDF2
import curses

def extract_pdf_metadata(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        metadata = reader.metadata
    return {key: metadata[key] for key in metadata}

def save_pdf_metadata(file_path, metadata):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata(metadata)
        
        with open(file_path, 'wb') as output_file:
            writer.write(output_file)

def main(stdscr, file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    metadata = extract_pdf_metadata(file_path)
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
        for idx, key in enumerate(keys):
            value = metadata[key]
            display_text = f"{key}: {value}"
            stdscr.addstr(idx, 0, display_text)

        if quitting_menu:
            # Display "Quit menu" in the footer
            stdscr.addstr(height - 1, 0, f"Quit menu {quit_key}", curses.A_REVERSE)
        elif editing:
            # Display "Editing" in the footer
            stdscr.addstr(height - 1, 0, "Editing", curses.A_REVERSE)

        # Draw the cursor
        if editing:
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
            if editing:
                cursor_position = len(keys[0]) + 2 if keys else 0
            else:
                cursor_position = 0

        elif editing:
            key = keys[cursor_line]
            value = metadata[key]
            max_cursor_position = len(key) + 2 + len(value)

            if ch == curses.KEY_DOWN and cursor_line < len(keys) - 1:
                cursor_line += 1
                cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(metadata[keys[cursor_line]]))
            elif ch == curses.KEY_UP and cursor_line > 0:
                cursor_line -= 1
                cursor_position = min(cursor_position, len(keys[cursor_line]) + 2 + len(metadata[keys[cursor_line]]))
            elif ch == curses.KEY_LEFT and cursor_position > len(key) + 2:
                cursor_position -= 1
            elif ch == curses.KEY_RIGHT and cursor_position < max_cursor_position:
                cursor_position += 1
            elif ch == 127:  # Backspace key
                if cursor_position > len(key) + 2:
                    metadata[key] = value[:cursor_position - len(key) - 3] + value[cursor_position - len(key) - 2:]
                    cursor_position = max(cursor_position - 1, len(key) + 2)
            elif ch == 330:  # Delete key
                if cursor_position < max_cursor_position:
                    metadata[key] = value[:cursor_position - len(key) - 2] + value[cursor_position - len(key) - 1:]
            elif ch < 256:
                metadata[key] = value[:cursor_position - len(key) - 2] + chr(ch) + value[cursor_position - len(key) - 2:]
                cursor_position += 1

    stdscr.clear()
    stdscr.refresh()

    if quit_key == ":x":
        save_pdf_metadata(file_path, metadata)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]
    curses.wrapper(main, file_path)
