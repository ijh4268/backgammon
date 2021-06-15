from abc import ABCMeta, abstractmethod
from contracts.interface import ContractNotRespected, ContractException
from parse_data import get_moves_from_turn, create_moves
from constants import *
from contracts import contract, new_contract, check
from sort import sort
from collections import Counter
from func_timeout import func_timeout
import json, random, uuid


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
        if CPos(move[0]) and CPos(move[1]):
            continue
        else: return False
    return True

@new_contract
def ValidateTurns(turns):
  if type(turns) == list:
    if len(turns) == 0: return True
    for turn in turns:
      if type(turn) == list:
        result = CPos(turn[0]) and CPos(turn[1])
      else: result = False
  else: result = False
  return result

@new_contract
def ValidateTurnData(data):
  return type(data) == dict and TURN in data.keys() and ValidateTurns(data[TURN])
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
    self.posns = sort(posns, 'board')

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
    if move.src_cpos == BAR: return self.bar() > move.dest_cpos
    if move.dest_cpos == HOME: return move.src_cpos > self.home()
    else: return move.src_cpos > move.dest_cpos
  def farthest(self):
    only_nums = list(filter(lambda x: type(x) == int, self.posns))
    if only_nums:
      return max(only_nums)
    else: return False
  def get_dist_from_home(self, cpos):
    if cpos == BAR: return self.bar()
    elif cpos == HOME: return self.home()
    else: return cpos
  def get_destination(self, posn, die):
    die = die * self.dir_of_travel()
    if posn == BAR:
      return self.bar()+die
    elif posn == HOME or posn + die <= self.home() : return HOME
    else: return posn + die
  
class White(Color):
  def __init__(self, posns=WHITE_INIT):
    self.posns = sort(posns, 'board')

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
    if move.src_cpos == BAR: return self.bar() < move.dest_cpos
    if move.dest_cpos == HOME: return move.src_cpos < self.home()
    else: return move.src_cpos < move.dest_cpos
  def farthest(self):
    only_nums = list(filter(lambda x: type(x) == int, self.posns))
    if only_nums:
      return min(only_nums)
    else: return False
  def get_dist_from_home(self, cpos):
    if cpos == HOME: return self.bar()
    elif cpos == BAR: return self.home()
    else: return self.home() - cpos
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
  @contract(color='$Color', src_cpos='CPos', dest_cpos='CPos')
  def __init__(self, color, src_cpos, dest_cpos):
    self.color = color
    self.src_cpos = src_cpos
    self.dest_cpos = dest_cpos
    self.as_list = [self.src_cpos, self.dest_cpos]

  def get_distance(self):
    if self.src_cpos == BAR:
      return abs(self.dest_cpos - self.color.bar()) 
    if type(self.src_cpos) == int and type(self.dest_cpos) == int:
      return abs(self.src_cpos - self.dest_cpos)
    if self.dest_cpos == HOME:
      return abs(self.src_cpos - self.color.home())
    
  def to_json(self):
    return json.dumps([self.color.name, self.src_cpos, self.dest_cpos])
# ============================================================================
class Dice(object):
  @contract(values='ValidateDice|list[0]')
  def __init__(self, values=[]):
    self.values = values
    self.original_combos = self.combos()
    self.original_values = values.copy()
  
  def roll(self):
    self.values = [random.randint(1, 6) for i in range(0, 2)]
    if self.values[0] == self.values[1]:
      self.values = [self.values[0] for i in range(0, 4)]
    self.original_combos = self.combos()

  def combos(self):
    if len(self.values) == 2:
      combos = self.values + [sum(self.values)]
    elif len(self.values) > 2:
      combos = [value * mult for value, mult in zip(self.values, range(1, len(self.values) + 1))]
    else:
      combos = self.values
    return sorted(combos, reverse=True)
  
  def reset(self):
    return Dice(self.original_values)

# ============================================================================
class Board(object):
  @contract (black_posns='list[15](int|str)|None', white_posns='list[15](int|str)|None')
  def __init__(self, black_posns=None, white_posns=None):
    if black_posns and white_posns:
      self.black = Black(black_posns)
      self.white = White(white_posns)
    else:
      self.black = Black()
      self.white = White()
      
    self.special_feature = 'board'

  def as_dict(self):
    return {BLACK:self.black.posns, WHITE:self.white.posns}

  def to_json(self):
    return json.dumps(self.as_dict())

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
      if self.is_bop(move):
        self.make_move(move)
        opponent = self._get_opponent(move.color)
        self.bop(opponent, move.dest_cpos)
      else: self.make_move(move)

  # Querys the board and returns the number of pieces in a particular cpos
  @contract(query='$Query', returns='int')
  def query(self, query):
    posns = query.color.posns
    return posns.count(query.cpos)

  # Checks to see if the game is over
  @contract(returns='bool')
  def finished(self):
    black_query = Query(self.black, HOME)
    white_query = Query(self.white, HOME)

    if self.query(black_query) == 15 or self.query(white_query) == 15:
      return True
    else:
      return False

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
    posns.remove(move.src_cpos)
    posns.append(move.dest_cpos)
    self._sort_board()

  @contract(move='$Move')
  def undo(self, move):
    color = self.get_color(move.color)
    posns = color.posns
    posns.remove(move.dest_cpos)
    posns.append(move.src_cpos)
    self._sort_board()

  # Checks if there is a checker in the src position (given by the Move object)
  @contract(move='$Move', returns='bool')
  def src_exists(self, move):
    color = self.get_color(move.color)
    posns = color.posns
    if move.src_cpos in posns:
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
    and move.src_cpos == color.farthest() or self.query(Query(color, HOME)) == 15:
      return True
    else:
      return False

  # checks if the given move is valid given the dice
  @contract(move='$Move', dice='$Dice', die='int', returns='bool')
  # Have variable to determine direction of travel, then multiply by dice value (get rid of add/sub)
  def is_valid_move(self, move, dice, die):
    player = move.color
    if not player.correct_dir(move): return False

    opponent = self._get_opponent(player)
    query = Query(opponent, move.dest_cpos)
    num_opponents = self.query(query) if move.dest_cpos != HOME else 0
    dist = move.get_distance()
    
    # if the player is trying to go home but cannot bear off, the move is invalid
    if move.dest_cpos == HOME and not self.can_bear_off(player): return False
    if move.dest_cpos == HOME and self._bear_off(move, dice): return True
    # Handle case where value of dice exceeds furthest checker that can bear off
    elif dist == die and num_opponents <= 1:
      return True
    else:
      return False
  
  @contract(color='$Color', dice='$Dice', turn='ValidateTurn')
  def play_move(self, color, dice, turn):
    color = self.get_color(color)
    all_turns = list(self.get_possible_turns(color, dice))
    valid_turns = self._uses_all_dice(all_turns)

    if turn and not valid_turns:
      return False
    elif not turn and not valid_turns:
      return self
    elif turn in valid_turns:
      get_moves_from_turn(turn, color)
      moves = create_moves(turn)
      self.make_moves(moves)
      return self
    else:
      return False
      
  def _uses_all_dice(self, all_turns):
    if all_turns:
      max_length = len(max(all_turns, key=len))
      return list(filter(lambda x: len(x) == max_length, all_turns))
    
  # Checks if there are any remaining legal moves left given that there are still dice remaining to use
  @contract(color='$Color', dice='$Dice')
  def get_possible_turns(self, color, dice, valid_turn=[]):
    color = self.get_color(color)
    unique_posns = list(Counter(color.posns).keys())
    unique_dice = list(Counter(dice.values).keys())
    if BAR in unique_posns: unique_posns = [BAR] 
    if valid_turn: yield valid_turn
    for src in unique_posns:
      for die in unique_dice:
        if src == HOME: continue # if the checker is already home, the we can skip
        dest = color.get_destination(src, die)
        move = Move(color, src, dest)
        if self.is_valid_move(move, dice, die):
          new_valid_turn = valid_turn + [[src, dest]]
          dice.values.remove(die)
          self.make_move(move)
          yield from self.get_possible_turns(color, dice, new_valid_turn)
          dice.values.append(die)
          self.undo(move)
        else: continue
# ============================================================================
class Player(object):
  def __init__(self, name):
    self.name = name
    self.started = False
    self.color = None
    self.opponent = None
    self.is_remote = False
    self.has_failed = False
    self.ident = uuid.uuid4()
    self.is_cheater = False

  @contract(color='str', opponent_name='str')
  def start_game(self, color, opponent_name):
    if not self.started: self.started = True
    else: raise RuntimeError('start_game was called twice before end_game')
    self.opponent = opponent_name
  
  @contract(board='$Board', dice='$Dice')
  def turn(self, board, dice):
    all_turns = list(board.get_possible_turns(self.color, dice))
    valid_turns = board._uses_all_dice(all_turns)
    turn = self.get_turn(board, valid_turns)
    original_turn = turn.copy()
    board.play_move(self.color, dice, turn)

  def is_winner(self, board):
    color = board.get_color(self.color)
    if color.posns.count(HOME) == 15: return True
    else: return False

  @contract(board='$Board', has_won='bool')
  def end_game(self, board, has_won):
    self.started = False
    self.has_won = has_won
    self.final_board = board
  
class RandomPlayer(Player):
  def __init__(self, name):
    super().__init__(name)
    self.color
    self.opponent

  def get_turn(self, board, valid_turns):
    if valid_turns: return random.choice(valid_turns)
    else: return []

class BopPlayer(Player):
  def __init__(self, name):
    super().__init__(name)
    self.color
    self.opponent

  #TODO: Change to use all generated boards
  def get_turn(self, board, valid_turns):
    max_score = 0
    max_index = 0
    if valid_turns:
      if len(valid_turns) < 1000:
        for turn in valid_turns:
          for move in turn:
            curr_move = Move(self.color, move[0], move[1])
            if board.is_bop(curr_move):
              score = self.color.get_dist_from_home(curr_move.src_cpos) - board._get_opponent(self.color).get_dist_from_home(curr_move.dest_cpos)
              if score > max_score:
                max_score = 0
                max_index = valid_turns.index(turn)
        return valid_turns[max_index]
      else: return random.choice(valid_turns)
    else: return []

class RemotePlayer(Player):
  def __init__(self, client):
    self.client = client
    try:
      msg = json.dumps('name')
      self.client.send(msg.encode() + '\n'.encode())
      data = json.loads(client.recv(1024).decode())
      check('ValidateNameData', data)
      name = data[NAME]
    except ContractNotRespected:
      self.client.close()

    super().__init__(name)
    self.color = None
    self.opponent
    
  @contract(color='str', opponent_name='str')
  def start_game(self, color, opponent_name):
    if not self.started: self.started = True
    else: raise RuntimeError('start_game was called twice before end_game')
    self.client.send(json.dumps({START: [color, opponent_name]}).encode() + '\n'.encode())
    msg = json.loads(self.client.recv(1024).decode())
    if msg == OKAY: return
    else: 
      self.cheater()
      return

  @contract(board='$Board', dice='$Dice')
  def turn(self, board, dice):
    try:
      self.client.send(json.dumps({TAKE_TURN: [board.as_dict(), dice.values]}).encode() + '\n'.encode())
      data = json.loads(self.client.recv(1024).decode())
      check('ValidateTurnData', data)
      turn = data[TURN]
      if board.play_move(self.color, dice, turn):
        pass
      else:
        self.cheater()
        return
         # ! if a player cheats, admin shuts down game and returns cheater (so tournament manager can edit bracket)
    except ContractNotRespected or ContractException:
        self.cheater()
        return

  @contract(board='$Board', has_won='bool')
  def end_game(self, board, has_won):
    self.started = False
    self.client.send(json.dumps({END: [board.as_dict(), has_won]}).encode() + '\n'.encode())
    msg = json.loads(self.client.recv(1024).decode())
    if msg == OKAY: return
    else: 
      self.cheater()
      return
  
  def cheater(self):
    self.is_cheater = True
    self.client.close()
    
     
    