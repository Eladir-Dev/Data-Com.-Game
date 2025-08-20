"""
Aque se encuentra la logica de stratego
"""
import random
import socket_server
from socket_server import Player 
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


def create_board(user1: str, deck1: list[list[str]], user2: str, deck2: list[list[str]]):
  """
    This method take car of creating the board for both players
    Note: two boards are return because each player will see their units in the bottum, it is the same board in diferent perspectives 
    Parameters:
      Input: 
        player1 (object)
        player2 (object)
      Output:
        boards (an array of length 2 that contains the board for player 1 (idx 0) and the board for player 2 (idx 1))
  """
  # board = [["" for _ in range (10)]for _ in range (10)]
  team = random.uniform(0, 1) # the team is selected

  if  (team<1):
    deck1 = set_team("R", deck1) # R = team red
    deck2 = set_team("B", deck2) # B = team blue
  else:
    deck1 = set_team("B", deck1) # R = team red
    deck2 = set_team("R", deck2) # B = team blue

  board1 = set_board(1,deck1,deck2)
  board2 = set_board(2,deck1,deck2)

  boards = [board1, board2]
  #users = [user1, user2]

  return boards
    

def set_board(player: int, deck1: list[list[str]], deck2: list[list[str]]):
  """
    This method set the board for the decired player
  """
  board = [["" for _ in range (10)]for _ in range (10)]
  if player == 2:
    temp = deck1
    deck1 = deck2
    deck2 = temp
  if player >0 and player<3:
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
        if (element > 1 and element < 4) or (element > 6 and element < 9):
          board[row+4][element] = "XX"
        else:
          board[row+4][element] = "00"
  else:
    print(f"ERROR, incorect player value: {player}")
    exit()
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
  print("+===00====01====02====03====04====05====06====07====08====09=+")
  count = 0
  for row in board:
      print(f"{count} {row}")
      count+=1
  print("+============================================================+")
  
def main():
  """
  This main method is used to debug Stratego's logic
  """
  print("Creating decks...")
  deck1 = create_debug_deck()
  deck2 = create_debug_deck()
  print("Creating boards")
  boards = create_board("Player 1", deck1, "Player 2", deck2)
  print("Printing board for player 1")
  print_board(boards[0])
  print("Printing board for player 2")
  print_board(boards[1])


if __name__ == "__main__":
  main()
