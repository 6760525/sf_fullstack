# -*- coding: utf-8 -*-
"""Battleship.ipynb

# Imports and Constants
"""

#Imports
from random import randint

#Constants
CLASS_OF_SHIP = {4: 'Battleship', 3: 'Cruiser', 2: 'Destroyer', 1:'Submarine'}

# The game's square field size
FIELD_SIZE = 6
#FIELD_SIZE = 10

# The game's fleet structure: key - number of decks, value - number of ships
FLEET = {3: 1, 2: 2, 1: 4} 
#FLEET = {4:1, 3: 2, 2: 3, 1: 4}

VAXIS = [chr(i) for i in range(ord('A'), ord('A')+FIELD_SIZE+1)]

EMPTY_CHAR = chr(0x25CC)
SHIP_CHAR = chr(0x25A3)
CONTOUR_CHAR = chr(0x25AB) 
DAMAGE_CHAR = '\033[95m' + chr(0x25CF) + '\033[0m'
DESTROY_CHAR = '\033[91m' + chr(0x25A3) + '\033[0m'
MISS_CHAR = '\033[91m' + chr(0x29B8) + '\033[0m'

# empty circle 0x25CB

"""# Exceptions"""

# Classes of Exceptions:
class BoardOutException(BaseException):
  pass

class SpotBusyException(BaseException):
  pass

class OutOfSpaceException(BaseException):
  pass

"""# Dot class"""

# Dot is a class for coordinates on the game's field
class Dot:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def get_x(self):
    return self.x

  def get_y(self):
    return self.y

  # checks if a dot is on the board
  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

  def __add__(self, other):
    return Dot(self.x + other.x, self.y + other.y)

  def __str__(self):
    return f'{VAXIS[self.x]}{self.y + 1}'

"""# Ship class"""

# Ships
class Ship:
  def __init__(self, length, dot, dir=0):
    self.length = length
    self.dot = dot
    self.dir = dir
    self.lifes = length

  def dots(self):
    # Returns list of all ship's dots
    dots_list = []
    x = self.dot.get_x()
    y = self.dot.get_y()
    dx, dy = (0, 1) if self.dir == 1 else (1, 0)
    for i in range(self.length):
      dots_list.append(Dot(x + i * dx, y + i * dy))
    return(dots_list)

"""# Board class

"""

class Board:
  def __init__(self):
    self.field = [[EMPTY_CHAR] * FIELD_SIZE for _ in range(FIELD_SIZE)]
    self.adots = [] # list of dots available on the Board
    self.ships = [] # list of ships on the Board
    self.lifes = sum(FLEET.values()) # total number of dots occupied by alife ships

    for i in range(FIELD_SIZE):
      for j in range(FIELD_SIZE):
        self.adots.append(Dot(i,j))

  def add_ship(self, ship):
    # adds a Ship on the Board
    if self.adots == []:
      raise OutOfSpaceException

    sd = ship.dots()
    if all(d in self.adots for d in sd): # if all ship's dots are available
      self.adots = [d for d in self.adots if (d not in sd)] # reduce the number of available dots
      for d in sd: self.field[d.x][d.y] = SHIP_CHAR # put a ship char on the field
      self.ships.append(ship) # add the Ship on the Board
      self.contour(ship, True) # add contour of the Ship on the Board
    else:
      raise BoardOutException

  def contour(self, ship, full):
    # adds a contour (full or particular) of the ship on the Board's field
    for d in ship.dots():
      for i in (-1, 0, 1):
        for j in (-1, 0, 1):
          cx = d.get_x() + i
          cy = d.get_y() + j
          cd = Dot(cx, cy)
          if cd in self.adots:
            if full or abs(i+j) != 1:
              self.adots.remove(cd)
              if self.field[cx][cy] == EMPTY_CHAR:
                self.field[cx][cy] = CONTOUR_CHAR 

  def show_board(self, hid=False):
    if hid: print('\033[90m', end='')
    print('-' * (4 * FIELD_SIZE + 4))
    print('  ', end='')
    for i in range(1, len(self.field[0])+1): print(f' |{i:2}', end='')
    print(' |')
    print('-' * (4 * FIELD_SIZE + 4))
    for i in range(len(self.field)):
      print(f' {VAXIS[i]} | ', end='')
      for j in range(len(self.field[i])):
        print(f'{self.field[i][j]} | ', end='')
      print()
    print('-' * (4 * FIELD_SIZE + 4))
    print('\033[0m', end='')

  def show_boards(self, oppboard):
    print('\033[2J', end='') # clear the screen here
    print("This is your grid:", " " * 20, "This is your opponent's grid:")
    print('-' * (4 * FIELD_SIZE + 4), ' ' * 10,'-' * (4 * FIELD_SIZE + 4))
    print('  ', end='')
    for i in range(1, len(self.field[0])+1): print(f' |{i:2}', end='')
    print(' |', end='')
    print(' ' * 14, end='')
    for i in range(1, len(oppboard.field[0])+1): print(f' |{i:2}', end='')
    print(' |')
    print('-' * (4 * FIELD_SIZE + 4), ' ' * 10,'-' * (4 * FIELD_SIZE + 4))

    for i in range(len(self.field)):
      print(f' {VAXIS[i]} | ', end='')
      for j in range(len(self.field[i])):
        print(f'{self.field[i][j]} | ', end='')
      print(' ' * 10, f' {VAXIS[i]} | ', end='')
      for j in range(len(oppboard.field[i])):
        print(f'{oppboard.field[i][j]} | ', end='')
      print()

    print('-' * (4 * FIELD_SIZE + 4), ' ' * 10,'-' * (4 * FIELD_SIZE + 4))
    print(f'{len(self.ships)} ships afloat', ' ' * 24, f'{oppboard.lifes - len(oppboard.ships)} ships afloat')

  def out(self, dot):
    if dot.get_x() < 0 or dot.get_x() > FIELD_SIZE - 1 or dot.get_y() < 0 or dot.get_y() > FIELD_SIZE - 1:
      return(True)
    else:
      return(False)

  def busy(self, dot):
    if dot in self.adots:
      return(False)
    else:
      return(True)

  def find_ship(self, dot): # returns a Ship if a dot is assosiated with the Ship on the Board
    for each in self.ships:
      if dot in each.dots():
        return(each)
    return(False)

  def shot(self, dot): # returns a Ship if it is destroyed, True if it is damaged, and False if the shot missed the target
    ship = self.find_ship(dot)
    if ship:
      ship.lifes -= 1
      if ship.lifes > 0:
        return(True)
      else:
        return(ship)
    else:
      return(False)

"""# Tools"""

def parse(los):
  if len(los) == 1: x, y = (los[0][0].upper(), los[0][1:])
  elif len(los) > 1: x, y = (los[0].upper(), los[1])
  else: raise BoardOutException

  if x.isdigit() and 1 <= int(x) <= FIELD_SIZE: x = int(x) - 1
  elif x in VAXIS: x = VAXIS.index(x)
  else: raise BoardOutException

  if y.isdigit() and 1 <= int(y) <= FIELD_SIZE: y = int(y) - 1
  else: raise BoardOutException

  return(Dot(x, y))

"""# Player class"""

class Player:
  def __init__(self, board, oppboard):
    self.board = board
    self.oppboard = oppboard
    self.nextmovearound = None

  def ask(self):
    # the method will be inherited and redefined in the child classes
    pass

  def move(self):
    # returns a dot for shot
    return(self.ask())

class AI(Player):
  def ask(self):
    if self.nextmovearound is not None: 
      for dot in [Dot(-1, 0), Dot(1, 0), Dot(0, -1), Dot(0, 1)]:
        if (self.nextmovearound + dot) in self.oppboard.adots:
          return(self.nextmovearound + dot)
    else:
      # here is a simple AI logic based on a random shot
      dot = self.oppboard.adots[randint(0, len(self.oppboard.adots)-1)]
      return(dot)

class User(Player):
  def ask(self):
    while True:
      try:
        answer = input('Your turn [row, col] (:q to quit): ').split()
        if answer == [':q']: 
          return(Dot(-1, -1))
        else:
          dot = parse(answer)
        if self.oppboard.busy(dot): 
          print(f'Dot {dot} is not available for shot! Try again.')
          continue
      except ValueError:
        print(f'You have to enter coordinates as a letter (row) and a number (column)! Try again.')
      except BoardOutException:
        print(f'The dot is out of the Board! Try again.')
      else: return(dot)

"""# Game class"""

class Game:
  def __init__(self):
    self.user_board = Board()
    self.ai_board = Board()
    self.user_oppboard = Board()
    self.ai_oppboard = Board()

    self.user = User(self.user_board, self.user_oppboard)
    self.ai = AI(self.ai_board, self.ai_oppboard)
    self.players = [self.user, self.ai]

    self.turn = False
     
  def random_board(self, board, verbose=False):
    while len(board.ships) != board.lifes:
      board.adots, board.ships = [], []
      board.field = [[EMPTY_CHAR] * FIELD_SIZE for _ in range(FIELD_SIZE)]
      for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
          board.adots.append(Dot(i,j))

      for sub_fleet in list(FLEET.items()):
        for i in range(1, sub_fleet[1]+1):
          while True:
            try:
              if board.adots == []: raise OutOfSpaceException
              dot = board.adots[randint(0, len(board.adots)-1)]
              row, col, vh = dot.get_x(), dot.get_y(), randint(0, 1)
              board.add_ship(Ship(sub_fleet[0], dot, vh))
              break
            except SpotBusyException:
              if verbose: print('There is not enough space for the ship here! Try to rotate it.')
            except BoardOutException: 
              if verbose: print('This position is busy or out of the Board! You can try to put it horizontally.')
            except ValueError: 
              if verbose: print("It's required a letter or a number for the row and a number for the column at least! Try again.")
            except OutOfSpaceException: 
              if verbose: print('No free spots on the field! Try again.')
              break

  def manual_board(self):
    while len(self.user_board.ships) != self.user_board.lifes:
      self.user_board.adots, self.user_board.ships = [], []
      self.user_board.field = [[EMPTY_CHAR] * FIELD_SIZE for _ in range(FIELD_SIZE)]
      for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
          self.user_board.adots.append(Dot(i,j))

      print("Enter a letter for the row and a number for the column")
      print("Add a dash '-' at the end to place the ship horizontally. Don't use separators.")
      print("For example: 'B2-' will be located horizontally starting from B2")
      print()
      print('Here is your Board. Please put your ships on it (:q to quit):')

      self.user_board.show_board()

      for sub_fleet in list(FLEET.items()):
        for i in range(1, sub_fleet[1]+1):
          while True:
            try:
              if self.user_board.adots == []: raise OutOfSpaceException
              ship_data = input(f'{sub_fleet[0]}-deck ship #{i} ({CLASS_OF_SHIP[sub_fleet[0]]}): [row][col][direction]: ').upper()
              if ship_data == ':Q': return(False)
              if len(ship_data) < 2: raise ValueError
              row, col = [int(x) if x.isdigit() else VAXIS.index(x)+1 for x in ship_data[:2]]
              dir = 1 if ship_data[-1] == '-' else 0
              self.user_board.add_ship(Ship(sub_fleet[0], Dot(row-1, col-1), dir))
              self.user_board.show_board()
              break
            except SpotBusyException: print('There is not enough space for the ship here! Try to rotate it.')
            except BoardOutException: print('This position is busy or out of the Board! You can try to put it horizontally.')
            except ValueError: print("It's required a letter or a number for the row and a number for the column at least! Try again.")
            except OutOfSpaceException: 
              print('No free spots on the field! Try again.')
              break

  def loop(self):
    pronoun = ['You', 'AI']
    turn = ~(input('Do you want to start? [Y/n]').upper() != 'N')
  
    while True:
      move = self.players[turn].move() # get a dot to shoot
      if move == Dot(-1, -1): return(False)
      print(f'{pronoun[turn]} shot at the {move}.')
      shot = self.players[~turn].board.shot(move)
      if type(shot).__name__ == 'Ship':
        print(f'\033[91m{pronoun[turn]} sunk a {CLASS_OF_SHIP[shot.length]}!\033[0m')
        for each in shot.dots():
            self.players[~turn].board.field[each.get_x()][each.get_y()] = DESTROY_CHAR
            self.players[turn].oppboard.field[each.get_x()][each.get_y()] = DESTROY_CHAR
            self.players[~turn].board.contour(shot, True)
            self.players[turn].oppboard.contour(shot, True)
        self.players[~turn].board.ships.remove(shot)
        self.players[turn].oppboard.ships.append(shot)
        self.players[turn].nextmovearound = None
      else:
        if shot:
            self.players[~turn].board.field[move.get_x()][move.get_y()] = DAMAGE_CHAR
            self.players[turn].oppboard.field[move.get_x()][move.get_y()] = DAMAGE_CHAR
            self.players[~turn].board.contour(Ship(1, move, 0), False)
            self.players[turn].oppboard.contour(Ship(1, move, 0), False)
            self.players[turn].nextmovearound = move
            print(f'\033[91m{pronoun[turn]} hit a warship!\033[0m')
        else:
            self.players[~turn].board.field[move.get_x()][move.get_y()] = MISS_CHAR
            self.players[turn].oppboard.field[move.get_x()][move.get_y()] = MISS_CHAR
            self.players[turn].oppboard.adots.remove(move)
            print(f'\033[91m{pronoun[turn]} missed!\033[0m')
            turn = ~turn

      if type(move).__name__ != 'Dot':
        return(False)

      input('Press Enter to continue...')
      self.user_board.show_boards(self.user_oppboard)

      if len(self.user_board.ships) == 0:
        print('\033[91mAI won!!!\033[0m')
        return(True)
      elif len(self.ai_board.ships) == 0:
        print('\033[91mYou won!!!\033[0m')
        return(True)

  def start(self):
    if input('Do you need help to settle your fleet? [Y/n]').upper() != 'N':
      self.random_board(self.user_board)
    else:
      self.manual_board()
    
    if len(self.user_board.ships) != self.user_board.lifes:
      print('The game is cancelled!')
      return(False)
      
    self.random_board(self.ai_board)
    print('This is an AI board. For test purposes only!')
    self.ai_board.show_board(True)

    self.user_board.show_boards(self.user_oppboard)

    if self.loop():
      print('The game is over!')
    else:
      print('The game is cancelled!')

"""# Main"""



# Main
if __name__ == '__main__':
  game = Game()
  game.start()