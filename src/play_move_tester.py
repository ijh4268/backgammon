from constants import *
from contracts import ContractNotRespected
from backgammon import Board
from parse_json import parse_json
from parse_data import get_board, get_color, get_dice, get_turn, get_moves_from_turn, create_moves

import sys, json

try:
    data = parse_json()[0]

    board = get_board(data)
    color = get_color(data, board)
    dice = get_dice(data)
    turn = get_turn(data)

    get_moves_from_turn(turn, color)
    create_moves(turn)

    result = board.play_move(color, dice, turn)
except ContractNotRespected:
    result = False

result = board.to_json() if isinstance(result, Board) else json.dumps(result)

sys.stdout.flush()
sys.stdout.write(result)

