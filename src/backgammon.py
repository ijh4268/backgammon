from bg_contracts import *
from constants import *
from contracts import contract
from parse_data import get_moves_from_turn, create_moves
from sort import sort
from random import randint
import json

#----------------------------- Backgammon Classes ----------------------------

# ============================================================================
class Player(object):
  def __init__(self, name):
    self.name = name
  
  @contract(color='Color', opponent_name='str')
  def start_game(color, opponent_name):
    print('The game has started!')
    print(f'Your color is {color}')
    print(f'Your opponent\'s name is {opponent_name}')
  
  @contract(board='$Board', dice='$Dice', returns='list($Move)')
  def turn(board, dice):
    print('Take your turn.')

  @contract(board='$Board', has_won='bool')
  def end_game(board, has_won):
    print('Game over!')
    result_msg = 'won!' if has_won else 'lost!'
    print(f'You have ' + result_msg)
# ============================================================================
class Query(object):
  @contract(color='Color', cpos='CPos')
  def __init__(self, color, cpos):
    self.color = color
    self.cpos = cpos

  def to_json(self):
    return json.dumps([self.color, self.cpos])
# ============================================================================
class Move(object):
  @contract(color='Color', source_cpos='CPos', dest_cpos='CPos')
  def __init__(self, color, source_cpos, dest_cpos):
    self.color = color
    self.source_cpos = source_cpos
    self.dest_cpos = dest_cpos

  def to_json(self):
    return json.dumps([self.color, self.source_cpos, self.dest_cpos])
# ============================================================================
class Board(object):
  @contract (black_posns='list[15](int|str)', white_posns='list[15](int|str)')
  def __init__(self, black_posns=None, white_posns=None):
    if black_posns and white_posns:
      self.black_posns = black_posns
      self.white_posns = white_posns
    else:
      self.black_posns = BLACK_INIT
      self.white_posns = WHITE_INIT
      
    self.special_feature = 'board'
    self.board_contract = new_contract('board', 'list[15](int|str)')

  def to_json(self):
    return json.dumps({BLACK:self.black_posns, WHITE:self.white_posns})

  # Makes a sequence of moves
  @contract(moves='list($Move)')
  def make_moves(self, moves):
    for move in moves:
      self.make_move(move)
    # verify contracts are still upheld
    self.board_contract.check(self.black_posns)
    self.board_contract.check(self.white_posns)

  @contract(color='Color')
  def _get_posns(self, color):
    if color == BLACK: return self.black_posns
    if color == WHITE: return self.white_posns
  # Querys the board and returns the number of pieces in a particular cpos
  @contract(query='$Query')
  def query(self, query):
    posns = self._get_posns(query.color)
    return posns.count(query.cpos)
    
  @contract(move='$Move')
  def is_bop(self, move):
    opponent_color = self.color_check(move.dest_cpos)
    if opponent_color is None: return False
    query = Query(self.color_check(move.dest_cpos), move.dest_cpos)
    if self.color_check(move.dest_cpos) != move.color and self.query(query) == 1:
        return True
    else:
        return False

  # moves the piece of the given color and cpos to the BAR
  @contract(color='Color', cpos='CPos')
  def bop(self, color, cpos):
    posns = self._get_posns(color)
    posns.remove(cpos)
    posns.append(BAR)
    self._sort_board()

  # helper method to make sure the board is always sorted
  def _sort_board(self):
    self.black_posns = sort(self.black_posns, self.special_feature)
    self.white_posns = sort(self.white_posns, self.special_feature)
  
  # Makes a single move
  @contract(move='$Move')
  def make_move(self, move):
    posns = self._get_posns(move.color)
    posns.remove(move.source_cpos)
    posns.append(move.dest_cpos)
    self._sort_board()

    # verify contract is still upheld
    self.board_contract.check(self.black_posns)
    self.board_contract.check(self.white_posns)

  # Checks if there is a checker in the src position (given by the Move object)
  @contract(move='$Move', returns='bool')
  def src_exists(self, move):
    posns = self._get_posns(move.color)
    if move.source_cpos in posns:
        return True
    else:
        return False
  
  # Checks what color is currently occupying the given dst position
  @contract(pos='CPos', returns='Color|None')
  def color_check(self, pos):
    if pos in self.black_posns:
        return BLACK
    elif pos in self.white_posns:
        return WHITE
    else:
        return None
  
  # checks if the player can bear off
  @contract(color='Color', returns='bool')
  def can_bear_off(self, color):
    posns = self._get_posns(color)
    if color == BLACK: 
      home_quadrant = BLACK_HOME_QUAD
    if color == WHITE: 
      home_quadrant = WHITE_HOME_QUAD
    for cpos in posns:
      if cpos not in home_quadrant and cpos != HOME:
        return False
    return True

  # checks if the given move is valid given the dice
  @contract(move='$Move', dice='list[<=4](int)', returns='bool')
  # Have variable to determine direction of travel, then multiply by dice value (get rid of add/sub)
  # TODO: Refactor to remove copied code (visitor classes?, helper functions?, loops?)
  def is_valid_move(self, move, dice):
      posns = self._get_posns(move.color)
      curr_color = BLACK if move.color != WHITE else WHITE
      opp_color = WHITE if move.color != WHITE else BLACK
      if move.color == BLACK:
          query = Query(opp_color, move.dest_cpos)
          num_opponents = self.query(query) if move.dest_cpos != HOME else 0
          # Black player wants to move from BAR
          if move.source_cpos == BAR:
            dist = BLACK_BAR - move.dest_cpos  

          # Black player wants to move on board
          elif type(move.source_cpos) == int and type(move.dest_cpos) == int:
            dist = move.source_cpos - move.dest_cpos
          # Black player wants to move HOME
          elif move.dest_cpos == HOME and self.can_bear_off(move.color):
            dist = move.source_cpos
            # Handle case where value of dice exceeds furthest checker
            if dist not in dice \
            and max(dice) not in posns \
            and move.source_cpos == max(filter(lambda x: type(x) == int, posns)):
              dice.remove(max(dice))
              return True
          else:
            return False

      if move.color == WHITE:
          query = Query(BLACK, move.dest_cpos)
          num_opponents = self.query(query) if move.dest_cpos != HOME else 0
          # White player wants to move from the BAR
          if move.source_cpos == BAR: 
              dist = move.dest_cpos
          # White player wants to move on the board
          elif type(move.source_cpos) == int and type(move.dest_cpos) == int: 
              dist = move.dest_cpos - move.source_cpos
          # White player wants to move HOME
          elif move.dest_cpos == HOME and self.can_bear_off(move.color): 
              dist = WHITE_HOME - move.source_cpos
              # Handle case where value of dice exceeds furthest checker
              if dist not in dice \
              and max(dice) not in posns \
              and move.source_cpos == min(filter(lambda x: type(x) == int, posns)):
                dice.remove(max(dice))
                return True
          else:
              return False

      if dist in dice and num_opponents <= 1:
        dice.remove(dist)
        return True
      else:
        return False

  @contract(color='Color', dice='ValidateDice', turn='ValidateTurn')
  def play_move(self, color, dice, turn):
        
    for move in turn:
      posns = self._get_posns(color)

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
  
  def _play_move_helper(self, move, color, occupants):
    dst = move.dest_cpos
    if occupants == color or occupants == None or dst == HOME:
      self.make_move(move)
    # If your opponent only has one checker at the dst position, then the move is a 'bop'. 
    # Your piece takes the position and their piece is sent to the bar.
    elif occupants != color and self.is_bop(move):
      self.make_move(move)
      self.bop(occupants, dst)
    else:
      return False
    return True

  # Checks if there are any remaining legal moves left given that there are still dice remaining to use
  @contract(color='Color', dice='list[<=4](int)', returns='bool')
  def check_possible_moves(self, color, dice):
    posns = self._get_posns(color)
    potential_turn = []
    for die in dice:
      for posn in posns:
        if posn == HOME: continue # if the checker is already home, the we can skip

        if color == WHITE:
          # if there is a player on the bar, that's the only move we need to check
          if posn == BAR: 
            dest = WHITE_BAR+die
            potential_turn.append([posn, dest])
            break 
          else:
            # calculate potential destination move
            dest = posn+die if posn+die != WHITE_HOME else HOME

        if color == BLACK:
          # if there is a player on the bar, that's the only move we need to check
          if posn == BAR:
            dest = BLACK_BAR-die
            potential_turn.append([posn, dest])
            break
          else:
            # calculate potential destination move
            dest = posn-die if posn-die != BLACK_HOME else HOME

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

# class Dice(object):
#   def __init__(self):
#     self.values = [randint(1,6), randint(1,6)]
#     if self.values[0] == self.values[1]:
#         self.values.append(self.values[0])
#         self.values.append(self.values[0])
    
  
  


