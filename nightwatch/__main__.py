# Copyright (c) 2024 iiPython

# Initialization
def main() -> None:

    # Check urwid
    def invalid_urwid_distrib():
        exit("ERROR: Nightwatch requires urwid to have a specific unicode patch not currently included in upstream urwid.\n\n" \
            "To fix this, run:\npip install -U urwid@git+https://github.com/iiPythonx/urwid\n\n" \
            "and relaunch Nightwatch.")

    try:
        from urwid import is_iipython_urwid
        if not is_iipython_urwid:
            invalid_urwid_distrib()

    except ImportError:
        invalid_urwid_distrib()

    # Modules
    from argparse import ArgumentParser
    from nightwatch.client import start_client

    # Handle CLI options
    ap = ArgumentParser(
        prog = "nightwatch",
        description = "The chatting application to end all chatting applications.",
        epilog = "Copyright (c) 2024 iiPython\nhttps://github.com/iiPythonx/nightwatch"
    )
    ap.add_argument("-a", "--address", help = "the nightwatch server to connect to")
    ap.add_argument("-u", "--username", help = "the username to use")

    # Launch client
    args = ap.parse_args()
    start_client(args.address, args.username)
