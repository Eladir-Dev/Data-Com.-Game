# Data-Communications-Game
For a Data Communications course, several client-server socket games were made.

## Creators
* Eduardo J. Matos Pérez ([GitHub](https://github.com/Eladir-Dev))
* Guillermo Myers ([GitHub](https://github.com/cyan-wolf))

## Concept
This client-server app allows players to play one of several games. The two main games are:
* A turn-based strategy board game.
* A real-time word game.

In addition to these, there are two more secret games:
* A secret real-time racing game.
* A secret DLC (downloadable) singleplayer game with an engaging storyline and boss fight. This is related to the Data Communications course since we are downloading a game from the network.

## Running the app (Notes)
* **NOTE**: The app has two components: the client and the server. These two function as separate programs.
    - On a given machine, there should only be 1 server running at a time.
    - Various clients can run on a single machine.
* **NOTE**: To play any of the games (besides the secret DLC one), the client must first connect to a server.
* A client can connect to external machines running the server by connecting to their IP address.
* Both the client and server sub-projects use the `uv` package manager for managing dependencies and running each program.
    - It can be installed using the `pip install uv`command.
    - Installing using `pip` should allow using `uv` directly. You can check using the `uv --version` command.
    - If for some reason the above command fails even after installing with `pip`, you can use the `python -m uv` command instead of `uv` as a workaround.
          * You can check that the workaround works by running the `python -m uv --version` command.

## Running the app
* For running the client locally:
    - **NOTE**: Since most of the games are 2-player, to actually test any of them you should run these commands in two separate terminals to run multiple instances of the client.
    - Go to the `client` subdirectory of the `Data-Com.-Game` project.
    - Run the `uv run main.py` (or `python -m uv run main.py`) command.
* For running the server locally:
    - Go to the `server` subdirectory of the `Data-Com.-Game` project.
    - Run the `uv run main.py` (or `python -m uv run main.py`) command.
 
## Documentation
### Protocol
* [Link to the protocol documentation](docs/PROTOCOL.md).

### Client
To locally build the client documentation, navigate to the `client` subfolder and execute the `docs/build_docs.bat` (Windows) batch file. The script builds the documentation and generates an HTML file at `docs/_build/html/html/index.html`.

```sh
cd client
./docs/build_docs.bat
./docs/_build/html/html/index.html
```

## Tools
* Programming language: Python
* UI Framework: Pygame and pygame-menu.
* Package management: `uv`.
* Documentation: `sphinx`.
* Game engine (for the secret DLC game): Godot

## Attribution
* Music for the secret racing game:
    - Creator: [Wolfgang_](https://opengameart.org/users/wolfgang)
    - [Music](https://opengameart.org/content/skeleton-waltz-theme)
    - [License](https://creativecommons.org/licenses/by/4.0/)
