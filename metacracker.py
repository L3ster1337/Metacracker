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
    # PyPDF2 does not support editing metadata directly
    # There's no direct substitution for this functionality
    # If you decide to use a different library, implement saving functionality here
    pass

def main(stdscr, file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    metadata = extract_pdf_metadata(file_path)

    y = 0
    mode = "NORMAL"

    while True:
        stdscr.clear()

        # Display metadata
        for key, value in metadata.items():
            stdscr.addstr(y, 0, f"{key}: {value}")
            y += 1

        # NORMAL mode
        if mode == "NORMAL":
            stdscr.addstr(y, 0, "-- NORMAL --")
            c = stdscr.getch()

            if c == ord(":"):
                mode = "COMMAND"
                command = ""
        # COMMAND mode
        elif mode == "COMMAND":
            stdscr.addstr(y, 0, f":{command}")
            c = stdscr.getch()

            if c == ord("\n"):  # Enter key
                if command == "q!":
                    break
                elif command == "x":
                    # Save metadata
                    save_pdf_metadata(file_path, metadata)
                    break
                mode = "NORMAL"
            elif c == 8:  # Backspace
                command = command[:-1]
            else:
                command += chr(c)

        y = 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]
    curses.wrapper(main, file_path)
