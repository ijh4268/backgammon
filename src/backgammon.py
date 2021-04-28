from contracts import contract
from bg_contracts import *
from constants import *
from parse_data import get_moves_from_turn, create_moves
from sort import sort
from random import randint
import json

#----------------------------- Backgammon Classes ----------------------------
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

  @contract(color='Color', cpos='CPos')
  def _get_query(self, color, cpos):
    return Query(color, cpos)

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
    query = self._get_query(self.color_check(move.dest_cpos), move.dest_cpos)
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
    color = self.color_check(move.source_cpos)
    if color == move.color:
        return True
    else:
        return False
  
  # Checks what color is currently occupying the given dst position
  @contract(pos='CPos', returns='Color|None')
  def color_check(self, pos):
    if pos in self.black_posns:
        return BLACK
    if pos in self.white_posns:
        return WHITE
    else:
        return None
  
  # checks if the player can bear off
  @contract(color='Color', returns='bool')
  def can_bear_off(self, color):
    posns = self._get_posns(color)
    if color == BLACK: 
      home_quadrant = range(1, 7)
    if color == WHITE: 
      home_quadrant = range(19, 25)
    for cpos in posns:
      if cpos not in home_quadrant and cpos != HOME:
        return False
    return True

  # checks if the given move is valid given the dice
  @contract(move='$Move', dice='list[<=4](int)', returns='bool')
  def is_valid_move(self, move, dice):
      if move.color == BLACK:
          if move.source_cpos == BAR:
              dist = 25 - move.dest_cpos
              if dist in dice:
                  dice.remove(dist)
                  return True
          elif type(move.source_cpos) == int and type(move.dest_cpos) == int:
              dist = abs(move.dest_cpos - move.source_cpos)
              if dist in dice:
                  dice.remove(dist)
                  return True
          elif move.dest_cpos == HOME and self.can_bear_off(move.color):
              dist = move.source_cpos
              if dist in dice:
                  dice.remove(dist)
                  return True
          else:
              return False
      if move.color == WHITE:
          if move.source_cpos == BAR:
              dist = move.dest_cpos
              if dist in dice:
                  dice.remove(dist)
                  return True
          elif type(move.source_cpos) == int and type(move.dest_cpos) == int:
              dist = abs(move.source_cpos - move.dest_cpos)
              if dist in dice:
                  dice.remove(dist)
                  return True
          elif move.dest_cpos == HOME and self.can_bear_off(move.color):
              dist = move.source_cpos
              if dist in dice:
                  dice.remove(dist)
                  return True
          else:
              return False

  @contract(color='Color', dice='ValidateDice', turn='ValidateTurn')
  def play_move(self, color, dice, turn):
        
      posns = self._get_posns(color)
      for move in turn:

          occupants = self.color_check(move.dest_cpos)

          # If there is no checker at src, then the move is invalid
          if self.src_exists(move) and self.is_valid_move(move, dice):
              # If a player has checkers on the bar, that takes first priority
              if BAR in posns:
                if self._play_move_helper(move, color, occupants): continue
              else:
                if self._play_move_helper(move, color, occupants): continue
          else:
              return False
      
      # check if there are still moves possible
      if dice and self.check_possible_moves(color, dice):
        return False
      else:
        return self
  
  def _play_move_helper(self, move, color, occupants):
    src = move.source_cpos
    dst = move.dest_cpos
    if occupants == color or occupants == None:
      self.make_move(move)
    # If your opponent only has one checker at the dst position, then the move is a 'bop'. Your piece takes the position and their piece is sent to the bar.
    elif occupants != color and self.is_bop(move):
      self.make_move(move)
      self.bop(occupants, dst)
    else:
      return False
    return True

  @contract(color='Color', dice='list[<=4](int)', returns='bool')
  def check_possible_moves(self, color, dice):
    posns = self._get_posns(color)
    potential_turn = []
    for posn in posns:
      for die in dice:
        if color == WHITE:
          dest = posn+die if posn+die != 25 else HOME
          if not CPos(dest): continue
          potential_turn.append([posn, dest])
        if color == BLACK:
          dest = posn-die if posn-die != 0 else HOME
          if not CPos(dest): continue
          potential_turn.append([posn, dest])
    get_moves_from_turn(potential_turn, color)
    moves = create_moves(potential_turn)
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
    
  
  


