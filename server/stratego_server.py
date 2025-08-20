"""
Aque se encuentra la logica de stratego
"""
import random
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

Mariscal (1), General (1), Coronel (2), Comandante (2), Capitán (3), Teniente (4), Sargento (4), Minero (8), Explorador (8), Espía (1), Bomba (6) y Bandera (1). 


def create_board(user1: str, deck1: list[list[str]], user2: str, deck2: list[list[str]]):
  board = [["" for _ in range (10)]for _ in range (10)]
  team = random.uniform(0, 1)

  if  (team<1):
    deck1 = set_team("R", deck1) # R = team red
    deck2 = set_team("B", deck2) # B = team blue
  else:
    deck1 = set_team("B", deck1) # R = team red
    deck2 = set_team("R", deck2) # B = team blue

  for row in deck1:
    for element in row:
      board[row][element] = deck[row][element]

  temp = 9
  for row in deck2:
    for element in row:
      board[row + temp][element] = deck[row][element]
    temp = temp - 2

  for row in range(4..2):
    for element in row:
      if (element > 1 and element < 4) or (element > 6 and element < 9):
        board[row][element] = "XX"
      else:
        board[row][element] = "00"
    






def set_team(team: str, deck: list[list[str]]):
  for row in deck:
    for element in row:
      deck[row][element] = deck[row][element] + team
  return deck
  

#[0R][SR][FR][1R][9R]
#[0R][SR][FR][1R][9R]

def create_debug_deck():
  deck = [["" for _ in range (10)]for _ in range (4)]
  print(deck)

def print_board():
  pass

def main():
  """
  This main method is used to debug Stratego's logic
  """
  print("Hello their")
  create_debug_deck()


if __name__ == "__main__":
  main()
