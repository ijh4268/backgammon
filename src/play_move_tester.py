import json
import sys

from contracts import ContractNotRespected

from backgammon import Board
from parse_data import get_board, get_color, get_dice
from parse_json import parse_json

try:
    data = parse_json()[0]

    board = get_board(data[0])
    color = get_color(data[1], board)
    dice = get_dice(data[2])
    turn = data[3]

    result = board.play_move(color, dice, turn)
except ContractNotRespected:
    result = False

result = board.to_json() if isinstance(result, Board) else json.dumps(result)

sys.stdout.flush()
sys.stdout.write(result)

