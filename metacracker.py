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
    edit_key = ""
    delete_mode = False
    cursor_line = 0
    cursor_position = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Display metadata
        for idx, (key, value) in enumerate(metadata.items()):
            if idx == cursor_line:
                display_text = f"{key}: {value[:cursor_position]}|{value[cursor_position:]}"
                stdscr.addstr(idx, 0, display_text, curses.A_REVERSE)
            else:
                stdscr.addstr(idx, 0, f"{key}: {value}")

        if quitting_menu:
            # Display "Quit menu" in the footer
            stdscr.addstr(height - 1, 0, "Quit menu ", curses.A_REVERSE)
            stdscr.addstr(height - 1, 10, quit_key)
        elif editing:
            # Display "Editing" in the footer
            stdscr.addstr(height - 1, 0, "Editing", curses.A_REVERSE)

        ch = stdscr.getch()

        # Quitting menu
        if ch == 27:  # 27 is the ASCII code for the "Esc" key
            quitting_menu = True
        elif quitting_menu:
            if ch == 127:  # Backspace key
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
        elif ch == curses.KEY_IC:  # Insert key
            editing = not editing
            if editing:
                edit_key = next(iter(metadata)) if metadata else ""
                cursor_position = len(metadata[edit_key])
            else:
                edit_key = ""

        elif editing:
            if ch == curses.KEY_DOWN:
                cursor_line += 1
                if cursor_line >= len(metadata):
                    cursor_line = len(metadata) - 1
                cursor_position = min(cursor_position, len(metadata[edit_key]))
            elif ch == curses.KEY_UP:
                cursor_line -= 1
                if cursor_line < 0:
                    cursor_line = 0
                cursor_position = min(cursor_position, len(metadata[edit_key]))
            elif ch == curses.KEY_LEFT:
                cursor_position -= 1
                if cursor_position < 0:
                    cursor_position = 0
            elif ch == curses.KEY_RIGHT:
                cursor_position += 1
                if cursor_position > len(metadata[edit_key]):
                    cursor_position = len(metadata[edit_key])
            elif ch == 127:  # Backspace key
                if delete_mode:
                    metadata[edit_key] = metadata[edit_key][:cursor_position-1] + metadata[edit_key][cursor_position:]
                    cursor_position -= 1
                    if cursor_position < 0:
                        cursor_position = 0
                elif cursor_position > 0:
                    metadata[edit_key] = metadata[edit_key][:cursor_position-1] + metadata[edit_key][cursor_position:]
                    cursor_position -= 1
            elif ch == 10 or ch == 13:  # Enter key
                metadata[edit_key] = metadata[edit_key][:cursor_position] + "\n" + metadata[edit_key][cursor_position:]
                cursor_line += 1
                cursor_position = 0
            elif ch < 256:
                metadata[edit_key] = metadata[edit_key][:cursor_position] + chr(ch) + metadata[edit_key][cursor_position:]
                cursor_position += 1

        stdscr.refresh()

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
