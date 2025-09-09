# Data Communications Game - Stratego and Word Golf (DCG-SWG) Protocol

## Abstract
This document serves to explain the usage and syntax of the DCG-SWG protocol. The protocol is based around the sending of commands. 
There are two types of commands: client-bound and server-bound. Client-bound commands are sent by the server to the client and always start
with the `?` character. Server-bound commands are always sent by the client to the server and always start with the `!` character. The commands are 
sent as UTF-8 encoded strings. Commands start with their respective symbol along with the name of the command. Commands can also contain zero or more fields 
which follow the command name. Fields are delimited by a `:` symbol.

## Command Format
### Client-bound
`?<command name>:<field 1>:<field 2>:<field 3>`

### Server-bound
`!<command-name>:<field 1>:<field 2>:<field 3>`

## Game Commands

### Stratego Game Commands

#### Game Request Command
##### Format
`!game:stratego:<starting_deck>`

##### Description
Sent by the client to queue a Stratego game with the given starting deck.

---

#### Game Start Command
##### Format
`?game-start:stratego:{own_color}:{opponent_username}`

##### Description
Sent to both players at the start of a game. Contains a player's color (assigned by the server) and 
the username of the opponent.

---

#### Turn Info Command
##### Format
`?turn-info:{turn}:{board_repr}`

##### Description
Sent at the start of each turn by the server to each client. Lets each client know the 
color of the player who is allowed to move for the current turn. Also sends a representation 
of the current Stratego board. The 10 x 10 board from the server is flatted onto a 100 element array. 
Each element of the array is delimited by a `:` symbol and turned into a UTF-8 encoded string.

---

#### Move Result Command
##### Format
`"?move-result:{kind}:{row_atk}:{col_atk}:{row_def}:{col_def}`

##### Description
Sent by the server for letting the clients know the result of a move. In Stratego, different outcomes can occurr as a result 
of moves:
* A piece simply moves to an empty space (`kind = movement`).
* A piece attacks an opponent piece and defeats it (`kind = attack_success`).
* A piece attacks an opponent piece and gets defeated (`kind = attack_fail`).
* A piece attacks another piece and both the attacking and defending pieces get defeated (`kind = tie`).

This command also contains the position (row/column) of the attacking and defending pieces respectively. All this information 
can be used by the client to convey to the player what happened during a movement through the use of UI, sound effects, etc.

---

#### Move Command
##### Format
`!move:{from_row}:{from_col}:{to_row}:{to_col}`

##### Description
Sent by the client to convey the intention to move the piece at the position (`from_row`, `from_col`) to the position (`to_row`, `to_col`). 
The server and client use rows and columns for coordinates instead of x and y. If the client sends an invalid move (i.e. by trying to move an 
opponent's piece) the server ignores the request and continues waiting for a valid move.

---

#### Game Over Command
##### Format 1
`?game-over:winner-determined:{winner_color}`

##### Description 1
Sent by the server whenever a winner is determined in a Stratego match. The server 
sends the color of the player who won the match.

##### Format 2
`?game-over:abrupt-end`

##### Description 2
Sent by the server whenever a match abruptly ends. Such as when a player disconnects.

---

### Word Golf Game Commands

#### Game Request Command
##### Format
`!game:word_golf`

##### Description
Sent by the client to queue a Word Golf game.

---

#### Game Start Command
##### Format
`?game-start:word_golf:{opponent_username}`

##### Description
Sent by the server at the start of a game to let the player know the opponent's username.

---

#### ... Command
##### Format
`...`

##### Description
...

---

