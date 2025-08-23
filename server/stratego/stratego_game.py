from .stratego_types import StrategoColor, ROWS, COLS, DECK_ROWS
from .stratego_player import StrategoPlayer

from server_types import BUF_SIZE, row_col_to_flat_index

class StrategoGame:
    """
    Represents a Stratego game on the server. Used for core game logic.
    """

    def __init__(self, player1: StrategoPlayer, player2: StrategoPlayer):
        """
        Initializes the game with the given players. Note that the players objects already have 
        had their colors decided. Also, the players already have sent their usernames and starting decks.
        """

        # Initializes an empty board.
        self.board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        
        self.is_running = True
        self.turn: StrategoColor = 'r'

        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]

        # player color -> Player
        self.turn_map: dict[StrategoColor, StrategoPlayer] = { player.color: player for player in self.players } # type: ignore

        self.add_player_starting_decks_to_board()
        self.add_lakes_to_board()

        self.debug_print_board()


    def add_player_starting_decks_to_board(self):
        """
        Adds the players' starting decks to the board. Note, the starting decks are not validated in this method.
        """

        # Add red player deck.
        player = self.turn_map['r']
        deck_repr = player.starting_deck_repr.split(':')

        for r in range(DECK_ROWS):
            for c in range(COLS):
                deck_flat_idx = row_col_to_flat_index(r, c, COLS)

                # Mirror the rows to add the pieces starting from the bottom.
                self.board[-(r + 1)][c] = f"r{deck_repr[deck_flat_idx]}"

        # Add blue player deck.
        player = self.turn_map['b']
        deck_repr = player.starting_deck_repr.split(':')

        for r in range(DECK_ROWS):
            for c in range(COLS):
                deck_flat_idx = row_col_to_flat_index(r, c, COLS)

                # Mirror the columns to make sure the pieces are added in a way 
                # that makes sense from the blue player's perspective. If they were added without 
                # mirroring the columns, they would be mirrored when compared to the blue player's 
                # starting deck (from their POV). 
                self.board[r][-(c + 1)] = f"b{deck_repr[deck_flat_idx]}"


    def add_lakes_to_board(self):
        LAKE_ENCODING = 'XX'

        LAKE_POSITIONS = [
            (4, 2),
            (4, 3),
            (5, 2),
            (5, 3),

            (4, 6),
            (4, 7),
            (5, 6),
            (5, 7),
        ]

        for r, c in LAKE_POSITIONS:
            self.board[r][c] = LAKE_ENCODING


    def get_current_player(self) -> StrategoPlayer:
        """
        Gets the player that is currently allowed to move.
        """
        return self.turn_map[self.turn]


    def debug_print_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                print(self.board[r][c].ljust(3), end='')

            print()


    def get_board_socket_repr(self) -> str:
        """
        Gets a socket-friendly string format for the board.
        """

        flattened_board = [' ' for _ in range(ROWS * COLS)]

        for r in range(ROWS):
            for c in range(COLS):
                # Maps 2D coords to 1D coords on a flattened array.
                # A flat array is needed to send the board over the socket.
                flat_idx = row_col_to_flat_index(r, c, COLS)

                flattened_board[flat_idx] = self.board[r][c]

        return ':'.join(flattened_board)
    

    def run(self):
        """
        Runs the given game in a loop.
        """

        while self.is_running:
            # Send turn info.
            for player in self.players:
                data = f"?turn-info:{self.turn}:{self.get_board_socket_repr()}"
                player.conn.sendall(data.encode())

            # Wait for (valid) player response.
            while True:
                conn_to_process = self.get_current_player().conn
                data = conn_to_process.recv(BUF_SIZE).decode()

                if data.startswith("?move"):
                    fields = data.split(':')
                    from_row = int(fields[1])
                    from_col = int(fields[2])
                    to_row = int(fields[3])
                    to_col = int(fields[4])

                    could_move = self.process_move((from_row, from_col), (to_row, to_col))
                    if could_move:
                        # Break out of the loop if the move was valid and the board was updated.
                        break
                    else:
                        print(f"LOG: ({self.turn}) performed an invalid move")

                else:
                    print(f"ERROR: Invalid response '{data}'")

        # TODO: Send the ?move-result command to the players. 

        # TODO: Figure out how to get the result of the last move 
        # (i.e. if a piece got attacked, which one was defeated, if there was a tie, etc.)
        
        # TODO: Implement the rest of the game here...


    def process_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """
        Processes the given move. Returns `True` if the move was valid and the board 
        was updated. Otherwise, does nothing and returns `False`.
        """
        # TODO: Actually do this ^^^

        return False