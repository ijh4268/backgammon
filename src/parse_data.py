import backgammon as bg
from constants import *
from parse_json import parse_json
from contracts import contract
import sys

# data = parse_json()[0]

def parse_board(data):
  # get return type to call appropriate helper function
  if QUERY in data.keys():
    handle_query(data)
  elif BOARD in data.keys():
    handle_board(data)
  else:
    raise("invalid board operation")

def handle_query(data):
  # N.B.: get_moves will also return the query at the end of the set of moves -> this should be removed prior to operating on the rest of the moves
  board = get_board(data, QUERY)
  moves = get_moves(data, QUERY)

  # remove query from end of moves
  query_arr = moves.pop()
  query = bg.Query(query_arr[0], query_arr[1])

  # create move objects
  moves = create_moves(moves)

  # makes all the moves given
  board.make_moves(moves)

  # query the board
  query_result = board.query(query)

  sys.stdout.flush()
  sys.stdout.write(str(query_result))  
  
def handle_board(data):
  board = get_board(data, BOARD)
  moves = get_moves(data, BOARD)

  # create move objects
  moves = create_moves(moves)

  # make all moves given
  board.make_moves(moves)

  # get the board as json
  board_json = board.to_json()

  sys.stdout.flush()
  sys.stdout.write(board_json)

# ------------------- Data Methods -------------------

def get_board(board, return_type=None):
  white_checkers = board[WHITE]
  black_checkers = board[BLACK]
  return bg.Board(black_checkers, white_checkers)

def get_moves(data, return_type=None):
  moves = data[return_type][1:]
  return moves

@contract(turn='list(list(str|int))')
def get_moves_from_turn(turn, color):
  for move in turn:
    move.insert(0, color) 

@contract(color='str')
def get_color(color, board):
  if color == BLACK:
    return board.black
  elif color == WHITE: 
    return board.white
  else:
    raise('Invalid color input!')

@contract(values='list')
def get_dice(values):
  return bg.Dice(values)

@contract(data='list', returns='list(list[2](int|str))')
def get_turn(data):
  return data[3]

@contract(moves='list(list(*|int))')
def create_moves(moves):
  for i, move in enumerate(moves):
    moves[i] = bg.Move(move[0], move[1], move[2])
  return moves
  
#parse_board(data)
