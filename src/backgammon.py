from abc import ABCMeta, abstractmethod

from contracts.interface import ContractNotRespected
from parse_data import get_moves_from_turn, create_moves
from constants import *
from contracts import contract, new_contract
from copy import deepcopy
from sort import sort
import json, random

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
  # returns the name of the color
  @abstractmethod
  def name():
    pass
  # returns the value of the player's BAR
  @abstractmethod
  def bar():
    pass
  # returns the value of the player's HOME
  @abstractmethod
  def home():
    pass
  # return the range of values in the player's home board
  @abstractmethod
  def home_quadrant():
    pass
  # returns the direction the player travels on the board
  @abstractmethod
  def dir_of_travel():
    pass
  # returns whether or not the player is traveling in the right direction 
  @abstractmethod
  def correct_dir():
    pass
  # returns the position of the player farthest from HOME
  @abstractmethod
  def farthest():
    pass
  # returns the destination of the player given their current position and the die they wish to move by
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
    self.original_combos = self.combos()
  
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
  
  @contract(color='$Color')
  def get_color(self, color):
    if color.name() == BLACK: return self.black
    elif color.name() == WHITE: return self.white
    else: raise ContractNotRespected


  # Makes a sequence of moves
  @contract(moves='list($Move)')
  def make_moves(self, moves):
    for move in moves:
      self.make_move(move)
    # verify contracts are still upheld
    # self.board_contract.check(self.black.posns)
    # self.board_contract.check(self.white.posns)

  # Querys the board and returns the number of pieces in a particular cpos
  @contract(query='$Query', returns='int')
  def query(self, query):
    posns = query.color.posns
    return posns.count(query.cpos)
  
  # returns whether or not the given move is a bop
  @contract(move='$Move', returns='bool')
  def is_bop(self, move):
    player = self.get_color(move.color)
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
    color = self.get_color(move.color)
    posns = color.posns
    posns.remove(move.source_cpos)
    posns.append(move.dest_cpos)
    self._sort_board()

    # verify contract is still upheld
    # self.board_contract.check(self.black.posns)
    # self.board_contract.check(self.white.posns)

  # Checks if there is a checker in the src position (given by the Move object)
  @contract(move='$Move', returns='bool')
  def src_exists(self, move):
    color = self.get_color(move.color)
    posns = color.posns
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

  # 
  @contract(move='$Move', dice='$Dice', returns='bool')
  def _bear_off(self, move, dice):
    color = self.get_color(move.color)
    posns = color.posns
    if max(dice.values) not in posns \
    and move.source_cpos == color.farthest():
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

    # if the player is trying to go home but cannot bear off, the move is invalid
    if move.dest_cpos == HOME and not self.can_bear_off(player): return False
    
    if dist in dice.combos() and num_opponents <= 1:
      return True
    # Handle case where value of dice exceeds furthest checker that can bear off
    elif move.dest_cpos == HOME and self._bear_off(move, dice):
      return True
    else:
      return False

  @contract(color='$Color', dice='$Dice', turn='ValidateTurn', returns='bool|*')
  def play_move(self, color, dice, turn):
    if not turn: valid_moves = self.get_possible_moves(color, dice)
    for move in turn:
      color = self.get_color(color)
      posns = color.posns
      last_move = move
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
    
    # If there are valid moves, but no turn, then the turn is invalid
    if valid_moves and not turn: 
      return False
    # If there are valid moves and dice left over, check to see if more dice could have been used
    elif valid_moves and dice.values and self._can_use_more_dice(last_move, valid_moves, dice):
      return False
    else:
      return self

  @contract(last_move='$Move', valid_moves='list(list[2](int|str))', dice='$Dice', returns='bool')
  def _can_use_more_dice(self, last_move, valid_moves, dice):
    color = last_move.color
    for val in dice.values:
      for move in valid_moves:
        move_dest = move[1]
        # where we end up if we use the last die
        destination_next_die = color.get_destination(last_move.dest_cpos, val)
        # where we end up if we used the other dice values first
        destination_valid_move = color.get_destination(move_dest, max(dice.original_combos)-val)
        # if we end up in the same place, then we have no better move
        # or, if we end up at home with dice left over, then we could have used those dice before bearing off
        if destination_next_die != destination_valid_move \
        or (destination_valid_move == destination_next_die == HOME): return True
        else: return False

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
class Player(object):
  def __init__(self, name):
    self.name = name
    self.started = False

  @contract(color='str', opponent_name='str')
  def start_game(self, color, opponent_name):
    if not self.started: self.started = True
    else: raise RuntimeError('start_game was called before ')
    print('The game has started!')
    self.color = color
    print(f'Your color is {color}')
    self.opponent = opponent_name
    print(f'Your opponent\'s name is {opponent_name}')
  
  @contract(board='$Board', dice='$Dice', returns='list(list[2](int|str))|bool')
  def turn(self, board, dice):
    board_copy = deepcopy(board)
    dice_copy = deepcopy(dice)
    board_reset = deepcopy(board)
    dice_reset = deepcopy(dice)
    self.color = board_copy.get_color(self.color)
    while True:
      try:
        random_turn = self._try_moves(board_copy, dice_copy)
        assert board.play_move(self.color, dice, random_turn)
        return [move.as_list for move in random_turn]
      except AssertionError:
        board = deepcopy(board_reset) 
        board_copy = deepcopy(board_reset)
        dice = deepcopy(dice_reset)
        dice_copy = deepcopy(dice_reset)
        self.color = board_copy.get_color(self.color)
        continue

  @contract(board='$Board', dice='$Dice')
  def _generate_valid_moves(self, board, dice):
    valid_moves = board.get_possible_moves(self.color, dice)
    get_moves_from_turn(valid_moves, self.color)
    valid_moves = create_moves(valid_moves)
    return valid_moves

  @contract(board='$Board', dice='$Dice')
  def _try_moves(self, board, dice):
    turn = []
    while dice.values:
      valid_moves = self._generate_valid_moves(board, dice)
      if valid_moves:
        move = self._get_move(valid_moves, board, dice)
        turn.append(move)
        board.make_move(move)
      else: break
    return turn

  @contract(board='$Board', has_won='bool')
  def end_game(self, board, has_won):
    self.started = False
    print('Game over!')
    result_msg = 'won!' if has_won else 'lost!'
    print(f'You have ' + result_msg)

class RandomPlayer(Player):
  def __init__(self, name):
    super().__init__(name)
  
  @contract(valid_moves='list($Move)', board='$Board', dice='$Dice')
  def _get_move(self, valid_moves, board, dice):
    random_move = random.choice(valid_moves)
    distance = random_move.get_distance()
    if distance in dice.values:
      dice.values.remove(distance)
    else: dice.values.remove(max(dice.values))
    return random_move

class BopPlayer(Player):
  def __init__(self, name):
    super().__init__(name)

  @contract(valid_moves='list($Move)', board='$Board', dice='$Dice')
  def _get_move(self, valid_moves, board, dice):
    moves_distances = {move: move.get_distance() for move in valid_moves}
    result = None
    for move in valid_moves:
      if board.is_bop(move):
        result = move
    if not result:
      result = max(moves_distances, key=moves_distances.get)
      if list(moves_distances.values()).count(moves_distances[result]) == len(moves_distances) or \
      result.dest_cpos == HOME: result = random.choice(valid_moves)
    distance = moves_distances[result]
    if distance in dice.values:
      dice.values.remove(distance)
    else: dice.values.remove(max(dice.values))
    return result
