import backgammon as bg
from parse_data import *
from parse_json import parse_json
from contracts import ContractException
import sys, json, copy

data = parse_json()[0]

board = get_board(data)
color = get_color(data, board)
dice = get_dice(data)

bop_player = bg.BopPlayer('bop', color)

turn = bop_player.turn(board, dice)

turn = json.dumps(turn)
board_print = board.to_json()

sys.stdout.flush()
sys.stdout.write(turn)
sys.stdout.write(board_print)