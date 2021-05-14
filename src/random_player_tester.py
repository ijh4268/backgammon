import backgammon as bg
from parse_data import *
from parse_json import parse_json
import sys, json

data = parse_json()[0]

board = get_board(data[0])
color = get_color(data[1], board)
dice = get_dice(data[2])

random_player = bg.RandomPlayer('random')
random_player.color = color

turn = random_player.turn(board, dice)
if turn == False: 
  print('Failed!')

turn = json.dumps(turn)

sys.stdout.flush()
sys.stdout.write(turn)