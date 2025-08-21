
from .stratego_types import StrategoColor, ROWS, COLS, DECK_ROWS
from .stratego_player import StrategoPlayer

from server_types import BUF_SIZE

class StrategoGame:
    def __init__(self, player1: StrategoPlayer, player2: StrategoPlayer):
        self.board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        
        self.is_running = True
        self.turn: StrategoColor = 'r'

        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]

        # player color -> Player
        self.turn_map: dict[StrategoColor, StrategoPlayer] = { player.color: player for player in self.players } # type: ignore

        self.add_player_starting_decks_to_board()


    def add_player_starting_decks_to_board(self):
        # Add red player deck.
        player = self.turn_map['r']
        deck_repr = player.starting_deck_repr.split(':')

        for r in range(DECK_ROWS):
            for c in range(COLS):
                deck_flat_idx = r * DECK_ROWS + c % COLS
                self.board[-(r + 1)][c] = f"r{deck_repr[deck_flat_idx]}"

        # Add blue player deck.
        player = self.turn_map['b']
        deck_repr = player.starting_deck_repr.split(':')

        for r in range(DECK_ROWS):
            for c in range(COLS):
                deck_flat_idx = r * DECK_ROWS + c % COLS
                self.board[r][c] = f"b{deck_repr[deck_flat_idx]}"


    def get_current_player(self) -> StrategoPlayer:
        """
        Gets the player that is currently allowed to move.
        """
        return self.turn_map[self.turn]


    def get_board_socket_repr(self) -> str:
        flattened_board = [' ' for _ in range(ROWS * COLS)]

        for r in range(ROWS):
            for c in range(COLS):
                # Maps 2D coords to 1D coords on a flattened array.
                # A flat array is needed to send the board over the socket.
                flat_idx = r * ROWS + c % COLS

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