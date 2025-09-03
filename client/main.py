import main_game_ui
import sys
from stratego import deck_selection


def main():
    main_game_ui.start()

if __name__ == "__main__":

    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == "deck":
        deck_selection.main()