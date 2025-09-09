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

#### Game Start Command
##### Format
`!game:stratego:<starting_deck>`

##### Description
Sent by the client to queue a Stratego game with the given starting deck.

#### ... Command
##### Format
`...`

##### Description
...

### Word Golf Game Commands

#### Game Start Command
##### Format
`!game:word_golf`

##### Description
Sent by the client to queue a Word Golf game.

#### ... Command
##### Format
`...`

##### Description
...

