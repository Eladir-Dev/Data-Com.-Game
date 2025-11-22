import time

from .stratego_types import (
    parse_piece_from_encoded_str, 
    get_piece_value, 
    toggle_color,
    move_result_to_command,
    ROWS, 
    COLS, 
    DECK_ROWS, 
    MOVE_RESULT_VIEW_DURATION_SECS,
    StrategoColor, 
    StrategoMoveResult, 
    Pair, 
)
from .stratego_player import StrategoPlayer
from .stratego_game_result import StrategoGameResult

from server_types import row_col_to_flat_index, get_sign, ColorCode

from command_reader import ClientCommandReader

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

        self.result: StrategoGameResult | None = None

        self.command_reader = ClientCommandReader(
            connections=[p.conn for p in self.players],
            valid_cmd_prefixes=(
                '!move',
            ),
        )

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
        self.turn = toggle_color(self.turn)


    def get_current_player(self) -> StrategoPlayer:
        """
        Gets the player that is currently allowed to move.
        """
        return self.turn_map[self.turn]


    def debug_print_board(self): # codigo copiado y modificado de stratego_server
        """
            This method prints the board on terminal
            Parameters:
              board (the board tha will be printed)
          """
        print(f"{ColorCode.GREEN}+==00==01==02==03==04==05==06==07==08==09==+")
        for colom in range(10):
            print(f"{ColorCode.GREEN}{colom}", end=f"{ColorCode.RESET}")
            for row in range(10):
                if "R" in self.board[colom][row].upper():
                    print(ColorCode.RED, end="")
                elif "B" in self.board[colom][row].upper():
                    print(ColorCode.BLUE, end="")
                elif "X" in self.board[colom][row].upper():
                    print(ColorCode.CYAN, end="")
                if (self.board[colom][row] == ""):
                    print("  00", end="")

                else:
                    print(f"  {self.board[colom][row]}", end="")
                print(ColorCode.RESET, end="")
            print(f"{ColorCode.GREEN}  |{ColorCode.RESET}")

        print(f"{ColorCode.GREEN}+==========================================+", end=f"{ColorCode.RESET}\n")
        # for r in range(ROWS):
        #     for c in range(COLS):
        #         print(self.board[r][c].ljust(3), end='')
        #
        #     print()


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
        Runs the given game.
        """
        try:
            self.run_main_game_loop()

        # End the game if a connection error occurs.
        except ConnectionResetError:
            self.result = StrategoGameResult(None, abrupt_end=True)

        # Game ended.
        print("LOG: Stratego game ended")

        for player in self.players:
            # The result of the game must have been determined already.
            assert self.result

            try:
                # There is a winner.
                if self.result.winner is not None:
                    player.conn.sendall(f"?game-over:stratego:winner-determined:{self.result.winner}\\".encode())

                # The game abruptly ended before finishing normally.
                elif self.result.abrupt_end:
                    player.conn.sendall("?game-over:stratego:abrupt-end\\".encode())

                else:
                    print("ERROR: Unknown win condition")

            # Do not bother trying to send a game over message if the client's socket is disconnected.
            except ConnectionResetError: pass


    def run_main_game_loop(self):
        """
        Runs the main part of the game loop.
        """
        while self.is_running:
            # Send turn info.
            for player in self.players:
                data = f"?turn-info:{self.turn}:{self.get_board_socket_repr()}\\"
                player.conn.sendall(data.encode())

            move_result: StrategoMoveResult | None = None

            while move_result is None:
                for player_idx in range(len(self.players)):
                    move_result = self.handle_player_client_response(player_idx)

                    if move_result is not None:
                        break # early-exit out of for loop

            print(move_result)

            # Send the move result command to the players (this is for animating the results). 
            for player in self.players:
                player.conn.sendall(move_result_to_command(move_result).encode())
            
            # Wait a duration so that the client has time to display the sent move result to the user.
            if move_result.kind == 'movement':
                time.sleep(MOVE_RESULT_VIEW_DURATION_SECS / 2)
            else:
                time.sleep(MOVE_RESULT_VIEW_DURATION_SECS)

            # Toggle the turn.
            self.toggle_turn()


    def handle_player_client_response(self, player_idx: int) -> StrategoMoveResult | None:
        for data in self.command_reader.yield_commands(player_idx):
            player = self.get_current_player()

            if data.startswith("!move"):
                if player.color != self.turn:
                    username = self.turn_map[player.color].username # type: ignore
                    print(f"LOG: Player '{username}' ({player.color}) tried to move even though it was not their turn.")
                    return None # player cannot move if it's not their turn

                fields = data.split(':')
                from_row = int(fields[1])
                from_col = int(fields[2])
                to_row = int(fields[3])
                to_col = int(fields[4])

                move_result = self.process_move((from_row, from_col), (to_row, to_col))

                if move_result is None:
                    print(f"LOG: ({self.turn}) performed an invalid move")

                return move_result
                    
            else:
                print(f"ERROR: Invalid response '{data}'")
                return None # unknown command from client


    # TODO: This function needs more testing.
    def get_scout_long_range_path(self, from_pos: Pair, to_pos: Pair) -> list[Pair]:
        path: list[Pair] = []

        # The row and columns only need to change by 1 (or -1), so the
        # sign function is used.
        dr = get_sign(to_pos[0] - from_pos[0])
        dc = get_sign(to_pos[1] - from_pos[1])

        curr_pos = from_pos

        while curr_pos != to_pos:
            curr_pos = (curr_pos[0] + dr, curr_pos[1] + dc)
            path.append(curr_pos)

        # Don't include the last element since we only care about the in-between pieces.
        return path[:-1]


    def check_valid_movement(self, from_pos: Pair, to_pos: Pair) -> bool:
        r_from, c_from = from_pos
        r_to, c_to = to_pos

        dr = abs(r_to - r_from)
        dc = abs(c_to - c_from)

        can_move = True
        is_scout = False

        elem = self.board[r_from][c_from]
        if len(elem) == 2 and elem != 'XX':
            can_move = parse_piece_from_encoded_str(elem[1]) not in {'bomb', 'flag'}
            is_scout = parse_piece_from_encoded_str(elem[1]) == 'scout'

        if not can_move:
            return False

        # Diagonal movement, disallowed.
        elif dr == dc:
            return False
        
        # Scout movement.
        elif is_scout:
            # Disallow movement that involves going in BOTH the row and column directions.
            # The scout should only move forward.
            if dr != 0 and dc != 0:
                return False

            path = self.get_scout_long_range_path(from_pos, to_pos)

            # Check every position in the scout's path.
            for pos in path:
                elem = self.board[pos[0]][pos[1]]

                # If any in-between tile is non-empty (i.e. a lake or a piece), then the 
                # long range scout movement is not valid.
                if len(elem) == 2:
                    return False

            return True
        
        # Non-adjacent movement, disallowed.
        elif dr > 1 or dc > 1:
            return False
        
        else:
            return True


    def process_move(self, from_pos: Pair, to_pos: Pair) -> StrategoMoveResult | None:
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
            return None
        
        elif not self.check_valid_movement(from_pos, to_pos):
            return None
        
        # Prevent the player from moving lake or empty spaces.
        elif element_from in {"XX", ""}:
            return None
        
        # Prevent the player from moving into lakes.
        elif element_to == "XX":
            return None
        
        # Disallow pieces from the same color to attack each other.
        elif len(element_to) == 2 and element_from[0] == element_to[0]:
            return None
        
        # Disallow the player from moving pieces they don't own.
        elif element_from[0] != current_player.color:
            return None
        
        # Player is moving into an empty tile (valid).
        elif element_from[0] == current_player.color and element_to == "":
            self.board[from_pos[0]][from_pos[1]] = ""
            self.board[to_pos[0]][to_pos[1]] = element_from

            return StrategoMoveResult(kind='movement', attacking_pos=from_pos, defending_pos=to_pos)
        
        # The current player is attacking one of the opponent's pieces (valid).
        else:
            own_piece_name = parse_piece_from_encoded_str(element_from[1])
            own_piece_value = get_piece_value(own_piece_name)

            opp_piece_name = parse_piece_from_encoded_str(element_to[1])
            opp_piece_value = get_piece_value(opp_piece_name)

            # These conditions override the normal attack conditions.
            spy_attacking_marshal = own_piece_name == 'spy' and opp_piece_name == 'marshal'
            miner_attacking_bomb = own_piece_name == 'miner' and opp_piece_name == 'bomb'

            if own_piece_value > opp_piece_value or spy_attacking_marshal or miner_attacking_bomb:
                # Replace the defeated piece with the attacking player's piece.
                self.board[to_pos[0]][to_pos[1]] = element_from

                # Remove the attacking piece from its old position.
                self.board[from_pos[0]][from_pos[1]] = ""

                if opp_piece_name == 'flag':
                    winning_color: StrategoColor = element_from[0] # type: ignore
                    self.declare_winner(winning_color)

                move_result = StrategoMoveResult(kind='attack_success', attacking_pos=from_pos, defending_pos=to_pos)

            elif own_piece_value < opp_piece_value:
                # Remove the current player's piece.
                self.board[from_pos[0]][from_pos[1]] = ""

                move_result = StrategoMoveResult(kind='attack_fail', attacking_pos=from_pos, defending_pos=to_pos)

            else:
                # Remove both pieces.
                self.board[to_pos[0]][to_pos[1]] = ""
                self.board[from_pos[0]][from_pos[1]] = ""

                move_result = StrategoMoveResult(kind='attack_fail', attacking_pos=from_pos, defending_pos=to_pos)

            return move_result
        

    def declare_winner(self, winner: StrategoColor):
        """
        Ends the game and declares a winner.
        """
        print(f"LOG: Player `{self.turn_map[winner].username}` ({winner}) has won.")

        self.is_running = False
        self.result = StrategoGameResult(winner, abrupt_end=False)