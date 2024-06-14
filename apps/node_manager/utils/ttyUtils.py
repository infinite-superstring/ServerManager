control_keys = {
    'c': '\x03',  # Ctrl+C
    'd': '\x04',  # Ctrl+D
    'z': '\x1A',  # Ctrl+Z
    'a': '\x01',  # Ctrl+A
    'b': '\x02',  # Ctrl+B
    'e': '\x05',  # Ctrl+E
    'f': '\x06',  # Ctrl+F
    'g': '\x07',  # Ctrl+G
    'h': '\x08',  # Ctrl+H
    'i': '\x09',  # Ctrl+I
    'j': '\x0A',  # Ctrl+J
    'k': '\x0B',  # Ctrl+K
    'l': '\x0C',  # Ctrl+L
    'm': '\x0D',  # Ctrl+M
    'n': '\x0E',  # Ctrl+N
    'o': '\x0F',  # Ctrl+O
    'p': '\x10',  # Ctrl+P
    'q': '\x11',  # Ctrl+Q
    'r': '\x12',  # Ctrl+R
    's': '\x13',  # Ctrl+S
    't': '\x14',  # Ctrl+T
    'u': '\x15',  # Ctrl+U
    'v': '\x16',  # Ctrl+V
    'w': '\x17',  # Ctrl+W
    'x': '\x18',  # Ctrl+X
    'y': '\x19',  # Ctrl+Y
    '\x1b': '\x1b',  # Escape (Esc)
}

cursor_keys = {
    'ArrowUp': '\x1b[A',  # Up arrow
    'ArrowDown': '\x1b[B',  # Down arrow
    'ArrowRight': '\x1b[C',  # Right arrow
    'ArrowLeft': '\x1b[D',  # Left arrow
    'Home': '\x1bOH',  # Home key
    'End': '\x1bOF',  # End key
    'PageUp': '\x1b[5~',  # Page Up key
    'PageDown': '\x1b[6~',  # Page Down key
    'Insert': '\x1b[2~',  # Insert key
    'Delete': '\x1b[3~',  # Delete key
}

function_keys = {
    'F1': '\x1bOP',  # F1
    'F2': '\x1bOQ',  # F2
    'F3': '\x1bOR',  # F3
    'F4': '\x1bOS',  # F4
    'F5': '\x1b[15~',  # F5
    'F6': '\x1b[17~',  # F6
    'F7': '\x1b[18~',  # F7
    'F8': '\x1b[19~',  # F8
    'F9': '\x1b[20~',  # F9
    'F10': '\x1b[21~',  # F10
    'F11': '\x1b[23~',  # F11
    'F12': '\x1b[24~',  # F12
}

def handle_key_event(event):
    # Handling Ctrl, Alt, Shift separately
    if 'Ctrl' in event['modifiers'] and event['key'] in control_keys:
        self.terminal.send(control_keys[event['key']])
    elif 'Alt' in event['modifiers']:
        # Handle Alt keypresses if needed
        pass
    elif 'Shift' in event['modifiers']:
        # Handle Shift keypresses if needed
        pass
    elif event['key'] in function_keys:
        self.terminal.send(function_keys[event['key']])
    else:
        self.terminal.write(event['key'])