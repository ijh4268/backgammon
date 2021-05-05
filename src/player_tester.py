import backgammon as bg
from parse_data import *
from parse_json import parse_json
from contracts import ContractException
import sys, json, copy

data = parse_json()[0]

board = get_board(data)
color = get_color(data, board)
dice = get_dice(data)

random_player = bg.RandomPlayer('random', color)

turn = random_player.turn(board, dice)
if turn == False: 
  print('Failed!')

turn = json.dumps(turn)

sys.stdout.flush()
sys.stdout.write(turn)