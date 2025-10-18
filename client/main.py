import sys
from ui.main_game_ui import MainGameUI
from games.stratego import deck_selection


def main():
    main_ui = MainGameUI()
    main_ui.start()


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) == 0:
        main()

    # For testing out the custom deck selection functionality.
    elif args[0] == "deck":
        deck_selection.main()

    else:
        print(f"ERROR: unknown command arguments: {' '.join(args)}")