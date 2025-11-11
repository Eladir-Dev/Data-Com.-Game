import contextlib
import io

import socket_server
import sys

def main():
    socket_server.run()
    

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) == 0:
        main()

    elif args[0] == "host":
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            main() # run with no terminal

    else:
        print(f"ERROR: unknown command arguments: {' '.join(args)}")

