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

  @abstractmethod
  def get_destination():
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
  def dir_of_travel(self):
    return -1
  def correct_dir(self, move):
    if move.source_cpos == BAR: return self.bar() > move.dest_cpos
    if move.dest_cpos == HOME: return move.source_cpos > self.home()
    else: return move.source_cpos > move.dest_cpos
  def farthest(self):
    only_nums = filter(lambda x: type(x) == int, self.posns)
    return max(only_nums)
  def get_destination(self, posn, die):
    die = die * self.dir_of_travel()
    if posn == BAR:
      return self.bar()+die
    elif posn == HOME or posn + die <= self.home() : return HOME
    else: return posn + die
  def as_value(self, posn):
    if posn == BAR: return self.bar()
    if posn == HOME: return self.home()
    else: return posn
  

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
  def dir_of_travel(self):
    return 1
  def correct_dir(self, move):
    if move.source_cpos == BAR: return self.bar() < move.dest_cpos
    if move.dest_cpos == HOME: return move.source_cpos < self.home()
    else: return move.source_cpos < move.dest_cpos
  def farthest(self):
    only_nums = filter(lambda x: type(x) == int, self.posns)
    return min(only_nums)
  def get_destination(self, posn, die):
    die = die * self.dir_of_travel()
    if posn == BAR:
      return self.bar()+die
    elif posn == HOME or posn + die >= self.home(): return HOME
    else: return posn + die
  def as_value(self, posn):
    if posn == BAR: return self.bar()
    if posn == HOME: return self.home()
    else: return posn

     
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
    self.as_list = [self.source_cpos, self.dest_cpos]

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
class Dice(object):
  @contract(values='ValidateDice')
  def __init__(self, values):
    self.values = values
  
  def combos(self):
    if len(self.values) == 2:
      combos = self.values + [sum(self.values)]
    elif len(self.values) > 2:
      combos = [value * mult for value, mult in zip(self.values, range(1, len(self.values) + 1))]
    else:
      combos = self.values
    return sorted(combos, reverse=True)

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

  @contract(move='$Move', dice='$Dice', returns='bool')
  def _bear_off(self, move, dice):
    player = move.color
    posns = player.posns
    if max(dice.values) not in posns \
    and move.source_cpos == player.farthest():
      return True
    else:
      return False


  # checks if the given move is valid given the dice
  @contract(move='$Move', dice='$Dice', returns='bool')
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
    
    if dist in dice.combos() and num_opponents <= 1:
      return True
    # Handle case where value of dice exceeds furthest checker
    elif move.dest_cpos == HOME and self._bear_off(move, dice):
      return True
    else:
      return False

  @contract(color='$Color', dice='$Dice', turn='ValidateTurn')
  def play_move(self, color, dice, turn):
    if not turn: valid_moves = self.get_possible_moves(color, dice)
    original_combos = dice.combos()
    for move in turn:
      posns = color.posns
      curr_move = move
      occupants_next_die = self.color_check(move.dest_cpos)

      valid_moves = self.get_possible_moves(color, dice)
      # If there is no checker at src, then the move is invalid
      if self.src_exists(move) and move.as_list in valid_moves:
        valid_moves.remove(move.as_list)
        # If a player has checkers on the bar, that takes first priority
        if (BAR in posns and move.source_cpos == BAR) or (BAR not in posns):
          if self._play_move_helper(move, color, dice, occupants_next_die): continue
        else:
          return False
      else:
        return False
      
    # check if there are still moves possible
    if valid_moves and dice.values:
      for val in dice.values:
        for move in valid_moves:
          destination_next_die = color.get_destination(curr_move.dest_cpos, val)
          destination_valid_move = color.get_destination(move[1], max(original_combos)-val)
          if destination_next_die != destination_valid_move \
          or (destination_valid_move == destination_next_die == HOME):
              return False
    return self
  
  @contract(move='$Move', color='$Color', dice='$Dice', occupants='$Color|None')
  def _play_move_helper(self, move, color, dice, occupants):
    dst = move.dest_cpos
    distance = move.get_distance()
    if occupants == None or occupants.name() == color.name() or dst == HOME:
      self.make_move(move)
    # If your opponent only has one checker at the dst position, then the move is a 'bop'. 
    # Your piece takes the position and their piece is sent to the bar.
    elif self.is_bop(move):
      self.make_move(move)
      self.bop(occupants, dst)
    else:
      return False
    if distance in dice.values: dice.values.remove(distance)
    else: dice.values.remove(max(dice.values))
    return True

  # Checks if there are any remaining legal moves left given that there are still dice remaining to use
  @contract(color='$Color', dice='$Dice', returns='list(list[2](int|str))')
  def get_possible_moves(self, color, dice):
    posns = color.posns
    valid_moves = []
    for die in dice.values:
      potential_moves = []
      for posn in posns:
        if posn == HOME: continue # if the checker is already home, the we can skip
        dest = color.get_destination(posn, die)
        if posn == BAR: # if the checker is on the bar, we only check those
          potential_moves.append([posn, dest])
          break 
        # Verify the destination is a valid CPos 
        if CPos(dest): 
          potential_moves.append([posn, dest])
      # Generate moves from the potential turn
      get_moves_from_turn(potential_moves, color)
      moves = create_moves(potential_moves)
      # Check if the moves are valid
      for move in moves:
        if self.is_valid_move(move, dice) and move.as_list not in valid_moves:
          valid_moves.append(move.as_list)
    return valid_moves
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