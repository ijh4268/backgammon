import backgammon as bg
import sys
import json
from parse_data import *
from parse_json import parse_json

data = parse_json()[0]

board = get_board(data[0])
color = get_color(data[1], board)
dice = get_dice(data[2])

bop_player = bg.AIPlayer('bop')
bop_player.color = color

turn = bop_player.turn(board, dice)

turn = json.dumps(turn)

sys.stdout.flush()
sys.stdout.write(turn)