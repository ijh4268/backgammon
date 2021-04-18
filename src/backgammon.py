from contracts import contract, new_contract
from constants import *
from sort_backend import sort
import json

@new_contract
def Color(color):
  return color == BLACK or color == WHITE

@new_contract
def CPos(value):
  return value in range(1, 25) or value == HOME or value == BAR


class Query(object):
  @contract(color='Color', cpos='CPos')
  def __init__(self, color, cpos):
    self.color = color
    self.cpos = cpos

  def to_json(self):
    return json.dumps([self.color, self.cpos])

class Move(object):
  @contract(color='Color', source_cpos='CPos', dest_cpos='CPos')
  def __init__(self, color, source_cpos, dest_cpos):
    self.color = color
    self.source_cpos = source_cpos
    self.dest_cpos = dest_cpos

  def to_json(self):
    return json.dumps([self.color, self.source_cpos, self.dest_cpos])

class Board(object):
  @contract (black_posns='list[15](int|str)', white_posns='list[15](int|str)')
  def __init__(self, black_posns, white_posns):
    self.black_posns = black_posns
    self.white_posns = white_posns
    self.special_feature = 'board'
    self.board_contract = new_contract('board', 'list[15](int|str)')

  def to_json(self):
    return json.dumps({BLACK:self.black_posns, WHITE:self.white_posns})

  @contract(moves='list($Move)')
  def make_moves(self, moves):
    for move in moves:
      if move.color == BLACK:
        self.black_posns.remove(move.source_cpos)
        self.black_posns.append(move.dest_cpos)
      if move.color == WHITE:
        self.white_posns.remove(move.source_cpos)
        self.white_posns.append(move.dest_cpos)
    self.black_posns = sort(self.black_posns, self.special_feature)
    self.white_posns = sort(self.white_posns, self.special_feature)
    # verify contract is still upheld
    self.board_contract.check(self.black_posns)
    self.board_contract.check(self.white_posns)

  @contract(query='$Query')
  def query(self, query):
    if query.color == BLACK:
      return self.black_posns.count(query.cpos)
    if query.color == WHITE:
      return self.white_posns.count(query.cpos)



