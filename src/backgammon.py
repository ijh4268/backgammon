from abc import ABCMeta, abstractmethod
from parse_data import get_moves_from_turn, create_moves
from constants import *
from contracts import contract, new_contract
from sort import sort
import json

#---------------------------- Backgammon Contracts ---------------------------

@new_contract
def CPos(value):
  return value in range(1, 25) or value == HOME or value == BAR

@new_contract
def ValidateDice(dice):
    length_check = len(dice) == 2 or len(dice) == 4
    for die in dice:
        values_check = die in range(1, 7) 
    if len(dice) == 4:
        same_check = dice.count(dice[0]) == 4
        return length_check and values_check and same_check
    else:
        return length_check and values_check

@new_contract
def ValidateTurn(turn):
    for move in turn:
        if isinstance(move.color, Color) and CPos(move.source_cpos) and CPos(move.dest_cpos):
            continue
        else: return False
    return True

#----------------------------- Backgammon Classes ----------------------------
# ============================================================================
class Color(metaclass=ABCMeta):
  @abstractmethod
  def name():
    pass

  @abstractmethod
  def bar():
    pass

  @abstractmethod
  def home():
    pass

  @abstractmethod
  def home_quadrant():
    pass

  @abstractmethod
  def correct_dir():
    pass

  @abstractmethod
  def farthest():
    pass
# ============================================================================
class Black(Color):
  def __init__(self, posns=BLACK_INIT):
    self.posns = posns

  def name(self):
    return BLACK
  def bar(self):
    return BLACK_BAR
  def home(self):
    return BLACK_HOME
  def home_quadrant(self):
    return BLACK_HOME_QUAD
  def correct_dir(self, move):
    return move.dest_cpos < move.source_cpos
  def farthest(self):
    only_nums = filter(lambda x: type(x) == int, self.posns)
    return max(only_nums)

class White(Color):
  def __init__(self, posns=WHITE_INIT):
    self.posns = posns

  def name(self):
    return WHITE
  def bar(self):
    return WHITE_BAR
  def home(self):
    return WHITE_HOME
  def home_quadrant(self):
    return WHITE_HOME_QUAD
  def correct_dir(self, move):
    return move.source_cpos < move.dest_cpos
  def farthest(self):
    only_nums = filter(lambda x: type(x) == int, self.posns)
    return min(only_nums)
     
# ============================================================================
class Query(object):
  @contract(color='$Color', cpos='CPos')
  def __init__(self, color, cpos):
    self.color = color
    self.cpos = cpos

  def to_json(self):
    return json.dumps([self.color.name, self.cpos])
# ============================================================================
class Move(object):
  @contract(color='$Color', source_cpos='CPos', dest_cpos='CPos')
  def __init__(self, color, source_cpos, dest_cpos):
    self.color = color
    self.source_cpos = source_cpos
    self.dest_cpos = dest_cpos

  def get_distance(self):
    if self.source_cpos == BAR:
      return abs(self.dest_cpos - self.color.bar()) 
    if type(self.source_cpos) == int and type(self.dest_cpos) == int:
      return abs(self.source_cpos - self.dest_cpos)
    if self.dest_cpos == HOME:
      return abs(self.source_cpos - self.color.home())
    
  def to_json(self):
    return json.dumps([self.color.name, self.source_cpos, self.dest_cpos])
# ============================================================================
class Board(object):
  @contract (black_posns='list[15](int|str)', white_posns='list[15](int|str)')
  def __init__(self, black_posns=None, white_posns=None):
    if black_posns and white_posns:
      self.black = Black(black_posns)
      self.white = White(white_posns)
    else:
      self.black_posns = Black()
      self.white_posns = White()
      
    self.special_feature = 'board'
    self.board_contract = new_contract('board', 'list[15](int|str)')

  def to_json(self):
    return json.dumps({BLACK:self.black.posns, WHITE:self.white.posns})

  def _get_opponent(self, color):
    return self.black if color.name() == WHITE else self.white

  # Makes a sequence of moves
  @contract(moves='list($Move)')
  def make_moves(self, moves):
    for move in moves:
      self.make_move(move)
    # verify contracts are still upheld
    self.board_contract.check(self.black.posns)
    self.board_contract.check(self.white.posns)

  # Querys the board and returns the number of pieces in a particular cpos
  @contract(query='$Query')
  def query(self, query):
    posns = query.color.posns
    return posns.count(query.cpos)
    
  @contract(move='$Move')
  def is_bop(self, move):
    player = move.color
    occupants = self.color_check(move.dest_cpos)
    if occupants is None: return False
    query = Query(occupants, move.dest_cpos)
    if player.name() != occupants.name() and self.query(query) == 1:
        return True
    else:
        return False

  # moves the piece of the given color and cpos to the BAR
  @contract(color='$Color', cpos='CPos')
  def bop(self, color, cpos):
    posns = color.posns
    posns.remove(cpos)
    posns.append(BAR)
    self._sort_board()

  # helper method to make sure the board is always sorted
  def _sort_board(self):
    self.black.posns = sort(self.black.posns, self.special_feature)
    self.white.posns = sort(self.white.posns, self.special_feature)
  
  # Makes a single move
  @contract(move='$Move')
  def make_move(self, move):
    posns = move.color.posns
    posns.remove(move.source_cpos)
    posns.append(move.dest_cpos)
    self._sort_board()

    # verify contract is still upheld
    self.board_contract.check(self.black.posns)
    self.board_contract.check(self.white.posns)

  # Checks if there is a checker in the src position (given by the Move object)
  @contract(move='$Move', returns='bool')
  def src_exists(self, move):
    posns = move.color.posns
    if move.source_cpos in posns:
        return True
    else:
        return False
  
  # Checks what color is currently occupying the given dst position
  @contract(pos='CPos', returns='$Color|None')
  def color_check(self, pos):
    if pos in self.black.posns:
        return self.black
    elif pos in self.white.posns:
      return self.white
    else:
      return None
  
  # checks if the player can bear off
  @contract(color='$Color', returns='bool')
  def can_bear_off(self, color):
    for cpos in color.posns:
      if cpos not in color.home_quadrant() and cpos != HOME:
        return False
    return True

  @contract(move='$Move', dice='list[<=4](int)', returns='bool')
  def _bear_off(self, move, dice):
    player = move.color
    posns = player.posns
    if max(dice) not in posns \
    and move.source_cpos == player.farthest():
      return True
    else:
      return False


  # checks if the given move is valid given the dice
  @contract(move='$Move', dice='list[<=4](int)', returns='bool')
  # Have variable to determine direction of travel, then multiply by dice value (get rid of add/sub)
  # TODO: Refactor to remove copied code (visitor classes?, helper functions?, loops?)
  def is_valid_move(self, move, dice):
    player = move.color
    if not player.correct_dir(move): return False
    
    opponent = self._get_opponent(player)
    query = Query(opponent, move.dest_cpos)
    num_opponents = self.query(query) if move.dest_cpos != HOME else 0
    dist = move.get_distance()

    if move.dest_cpos == HOME and not self.can_bear_off(player): return False
    
    if dist in dice and num_opponents <= 1:
      dice.remove(dist)
      return True
    # Handle case where value of dice exceeds furthest checker
    elif move.dest_cpos == HOME and self._bear_off(move, dice):
      dice.remove(max(dice))
      return True
    else:
      return False

  @contract(color='$Color', dice='ValidateDice', turn='ValidateTurn')
  def play_move(self, color, dice, turn):
    for move in turn:
      posns = color.posns

      occupants = self.color_check(move.dest_cpos)

      # If there is no checker at src, then the move is invalid
      if self.src_exists(move) and self.is_valid_move(move, dice):
          # If a player has checkers on the bar, that takes first priority
          if (BAR in posns and move.source_cpos == BAR) or (BAR not in posns):
            if self._play_move_helper(move, color, occupants): continue
          else:
            return False
      else:
          return False
      
    # check if there are still moves possible
    if dice and self.check_possible_moves(color, dice):
      return False
    else:
      return self
  
  @contract(move='$Move', color='$Color', occupants='$Color|None')
  def _play_move_helper(self, move, color, occupants):
    dst = move.dest_cpos
    if occupants == None or occupants.name() == color.name() or dst == HOME:
      self.make_move(move)
    # If your opponent only has one checker at the dst position, then the move is a 'bop'. 
    # Your piece takes the position and their piece is sent to the bar.
    elif self.is_bop(move):
      self.make_move(move)
      self.bop(occupants, dst)
    else:
      return False
    return True

  # Checks if there are any remaining legal moves left given that there are still dice remaining to use
  @contract(color='$Color', dice='list[<=4](int)', returns='bool')
  def check_possible_moves(self, color, dice):
    posns = color.posns
    potential_turn = []
    for die in dice:
      for posn in posns:
        if posn == HOME: continue # if the checker is already home, the we can skip
        if posn == BAR: 
          dir = color.dir_of_travel()
          dest = color.bar()+(die * dir)
          potential_turn.append([posn, dest])
          break 
        else:
          # calculate potential destination move
          dir = color.dir_of_travel()
          dest = posn+(die * dir) if posn+(die * dir) != color.home() else HOME
        # Verify the destination is a valid CPos 
        if CPos(dest): 
          potential_turn.append([posn, dest])
    # Generate moves from the potential turn
    get_moves_from_turn(potential_turn, color)
    moves = create_moves(potential_turn)
    # Check if the moves are valid
    for move in moves:
      if self.is_valid_move(move, dice):
        return True
    return False
# ============================================================================
# class Player(object):
#   def __init__(self, name):
#     self.name = name
  
#   @contract(color='Color', opponent_name='str')
#   def start_game(color, opponent_name):
#     print('The game has started!')
#     print(f'Your color is {color}')
#     print(f'Your opponent\'s name is {opponent_name}')
  
#   @contract(board='$Board', dice='list', returns='list($Move)')
#   def turn(board, dice):
#     print('Take your turn.')

#   @contract(board='$Board', has_won='bool')
#   def end_game(board, has_won):
#     print('Game over!')
#     result_msg = 'won!' if has_won else 'lost!'
#     print(f'You have ' + result_msg)