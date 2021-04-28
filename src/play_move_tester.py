from bg_contracts import *
from constants import *

from backgammon import Board, Move
from parse_json import parse_json
from parse_data import get_board, get_color, get_dice, get_turn, get_moves_from_turn, create_moves

import sys, json

data = parse_json()[0]

board = get_board(data)
color = get_color(data)
dice = get_dice(data)
turn = get_turn(data)

get_moves_from_turn(turn, color)
create_moves(turn)

result = board.play_move(color, dice, turn)
result = board.to_json() if isinstance(result, Board) else json.dumps(result)

sys.stdout.flush()
sys.stdout.write(result)

'''
def __init__(self):
    self.values = [randint(1,6), randint(1,6)]
    if self.values[0] == self.values[1]:
        self.values.append(self.values[0])
        self.values.append(self.values[0])
'''
