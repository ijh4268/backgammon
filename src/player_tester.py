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

while True:
  try:
    turn = random_player.turn(copy.deepcopy(board), copy.deepcopy(dice))
    if turn == False: continue
  except ContractException:
    continue
  break

turn = json.dumps(turn)

sys.stdout.flush()
sys.stdout.write(turn)