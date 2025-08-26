from .stratego_types import StrategoColor, ROWS, COLS, DECK_ROWS, parse_piece_from_encoded_str, get_piece_value
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
        self.board = [['' for _ in range(COLS)] for _ in range(ROWS)]
        
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


    def toggle_turn(self):
        toggle = lambda t: 'r' if t == 'b' else 'b'
        self.turn = toggle(self.turn)


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

        flattened_board = ['' for _ in range(ROWS * COLS)]

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

                if data.startswith("!move"):
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

            # TODO: Send the ?move-result command to the players (this is for animating the results). 

            # TODO: Figure out how to get the result of the last move 
            # (i.e. if a piece got attacked, which one was defeated, if there was a tie, etc.)
            
            # TODO: Implement the rest of the game here...

            # Toggle the turn.
            self.toggle_turn()


    def check_valid_movement(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        r_from, c_from = from_pos
        r_to, c_to = to_pos

        dr = abs(r_to - r_from)
        dc = abs(c_to - c_from)

        can_move = True
        is_scout = False

        elem = self.board[r_from][c_from]
        if len(elem) == 2:
            can_move = parse_piece_from_encoded_str(elem[1]) not in {'bomb', 'flag'}
            is_scout = parse_piece_from_encoded_str(elem[1]) == 'scout'

        if not can_move:
            return False

        # Diagonal movement, disallowed.
        elif dr == dc:
            return False
        
        # Non-adjacent movement, disallowed.
        elif dr > 1 or dc > 1 and not is_scout:
            return False
        
        # Scout movement.
        elif is_scout:
            # TODO: Implement logic for not jumping over pieces.
            return True
        
        else:
            return True


    def process_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """
        Processes the given move. Returns `True` if the move was valid and the board 
        was updated. Otherwise, does nothing and returns `False`.
        """
        current_player = self.get_current_player()

        element_from = self.board[from_pos[0]][from_pos[1]]
        element_to = self.board[to_pos[0]][to_pos[1]]

        print(f"trying to move {from_pos} -> {to_pos}")
        print(f"`{element_from}` -> `{element_to}`")

        if from_pos == to_pos:
            return False
        
        elif not self.check_valid_movement(from_pos, to_pos):
            return False
        
        # Prevent the player from moving lake or empty spaces.
        elif element_from in {"XX", ""}:
            return False
        
        # Prevent the player from moving into lakes.
        elif element_to == "XX":
            return False
        
        # Disallow pieces from the same color to attack each other.
        elif len(element_to) == 2 and element_from[0] == element_to[0]:
            return False
        
        # Disallow the player from moving pieces they don't own.
        elif element_from[0] != current_player.color:
            return False
        
        # Player is moving into an empty tile (valid).
        elif element_from[0] == current_player.color and element_to == "":
            self.board[from_pos[0]][from_pos[1]] = ""
            self.board[to_pos[0]][to_pos[1]] = element_from

            return True
        
        # The current player is attacking one of the opponent's pieces (valid).
        else:
            own_piece_name = parse_piece_from_encoded_str(element_from[1])
            own_piece_value = get_piece_value(own_piece_name)

            opp_piece_name = parse_piece_from_encoded_str(element_to[1])
            opp_piece_value = get_piece_value(opp_piece_name)

            # TODO: Handle special cases (like those involving the spy, etc.).

            if own_piece_value > opp_piece_value:
                # Remove the opponent piece.
                self.board[to_pos[0]][to_pos[1]] = ""

            elif own_piece_value < opp_piece_value:
                # Remove the current player's piece.
                self.board[from_pos[0]][from_pos[1]] = ""

            else:
                # Remove both pieces.
                self.board[to_pos[0]][to_pos[1]] = ""
                self.board[from_pos[0]][from_pos[1]] = ""

            return True