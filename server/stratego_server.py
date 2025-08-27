"""
Aqui se encuentra la logica de stratego
"""
import random
import socket_server
from socket_server import StrategoPlayer 
from server_types import ColorCode
# El cliente (jugador) va a tener listo su deck antes de empezar el juego

# recoger queue 
# leer los decks
# prepara el tablero
# recoger comando
# empezar partida (el rojo empieza)

# Indice de tropas:
#   's' = Espía (Spy)
#   '1' = Explorador
#   '2' = Minero derrota a 'b'
#   '3' = Sargento
#   '4' = Teniente
#   '5' = Capitan
#   '6' = Comandante
#   '7' = Coronel
#   '8' = General
#   '9' = Mariscal derrota a todos, pwro es derotado por 's'
#   'b' = Bomba derrota a todo excepto a '2'
#   'f' = Bandera (flag) el que la capture gana

def create_board(user1: StrategoPlayer, user2: StrategoPlayer):
  """
    This method take car of creating the board for both players
    Note: two boards are return because each player will see their units in the bottum, it is the same board in diferent perspectives 
    Parameters:
      Input: 
        player1 (object)
        player2 (object)
      Output:
        returns a list containing [ user1: StrategoPlayer, user2: StrategoPlayer, board: list[list[str]] ]
  """
  # board = [["" for _ in range (10)]for _ in range (10)]
  team = random.uniform(0, 1) # the team is selected
  deck1 = user1.starting_deck_repr
  deck2 = user2.starting_deck_repr

  if  (team<1):
    user1.color = 'r'
    user2.color = 'b'
    deck1 = set_team("R", deck1) # R = team red
    deck2 = set_team("B", deck2) # B = team blue
  else:
    user1.color = 'b'
    user1.color = 'r'
    deck1 = set_team("B", deck1) # R = team red
    deck2 = set_team("R", deck2) # B = team blue

  board = set_board(deck1,deck2)

  output = [user1, user2, board]
  #users = [user1, user2]

  return output
    

def set_board(deck1: list[list[str]], deck2: list[list[str]]):
  """
    This method set the board for the decired player
  """
  board = [["" for _ in range (10)]for _ in range (10)]
  
  for row in range(4):
    for element in range(10):
      board[row][element] = deck1[row][element]

  temp = 9
  for row in range(4):
    for element in range(10):
      board[row + temp][element] = deck2[row][element]
    temp = temp - 2

  for row in range(2):
    for element in range(10):
      if (element > 1 and element < 4) or (element > 5 and element < 8):
        board[row+4][element] = "XX"
      else:
        board[row+4][element] = "00"

  return board




def set_team(team: str, deck: list[list[str]]):
  for row in range(4):
    for element in range(10):
      deck[row][element] = deck[row][element] + team
  return deck
  

#[0R][SR][FR][1R][9R]
#[0R][SR][FR][1R][9R]

def create_debug_deck():
  """
    This method creats a deck for debug pourposes
    Parameters:
      Output: 
        deck (array)
  """
  # deck = [["" for _ in range (10)]for _ in range (4)]
  # deck = [
  #   ['', '', '', '', '', '', '', '', '', '']
  #   ['', '', '', '', '', '', '', '', '', '']
  #   ['', '', '', '', '', '', '', '', '', '']
  #   ['', '', '', '', '', '', '', '', '', '']
  # ]
  # print(deck)

  # Define the limits for each character
  limits = {
      's': 1,
      '1': 8,
      '2': 5,
      '3': 4,
      '4': 4,
      '5': 4,
      '6': 3,
      '7': 2,
      '8': 1,
      '9': 1,
      'b': 6,
      'f': 1
  }

  # Create the deck (2D array)
  deck = [['' for _ in range(10)] for _ in range(4)]

  # Flatten the deck for easier filling
  flat_deck = [cell for row in deck for cell in row]

  # Create a list of items to fill the deck based on limits
  items_to_fill = []
  for item, limit in limits.items():
      items_to_fill.extend([item] * limit)

  # Shuffle the items to randomize their placement
  random.shuffle(items_to_fill)

  # Fill the deck
  for i in range(len(flat_deck)):
      if i < len(items_to_fill):
          flat_deck[i] = items_to_fill[i]

  # Convert the flat deck back to 2D
  for i in range(4):
      for j in range(10):
          deck[i][j] = flat_deck[i * 10 + j]

  return deck


def print_board(board: list[list[str]]):
  """
  This method prints the board on terminal
    Parameters:
  board (the board tha will be printed)
  """
  print(f"{ColorCode.GREEN}+==00==01==02==03==04==05==06==07==08==09==+")
  for colom in range(10):
    print(f"{ColorCode.GREEN}{colom}", end=f"{ColorCode.RESET}")
    for row in range(10):
        if "R" in board[colom][row].upper():
            print(ColorCode.RED, end="")
        elif "B" in board[colom][row].upper():
            print(ColorCode.BLUE, end="")
        if "X" in board[colom][row].upper():
            print(ColorCode.CYAN, end="")


        print(f"  {board[colom][row]}", end="")
        print(ColorCode.RESET, end="")
    print(f"{ColorCode.GREEN}  |{ColorCode.RESET}")

  print(f"{ColorCode.GREEN}+==========================================+", end=f"{ColorCode.RESET}\n")
  
def main():
  """
  This main method is used to debug Stratego's logic
  """
  print("Creating decks...")
  deck1 = create_debug_deck()
  deck2 = create_debug_deck()
  player1 = StrategoPlayer(None,"Player 1",deck1,None)
  player2 = StrategoPlayer(None,"Player 2",deck2,None)
  print("Creating boards")
  input = create_board(player1, player2)
  board = input[2]
  player1 = input[0]
  player2 = input[1]
  print("Printing board for player 1")
  print_board(board)
  print("Printing board for player 2")
  


if __name__ == "__main__":
  main()
