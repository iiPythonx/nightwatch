# Copyright (c) 2024 iiPython

# Initialization
def main() -> None:
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
