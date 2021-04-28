from contracts import new_contract
from constants import *

@new_contract
def Color(color):
  return color == BLACK or color == WHITE

@new_contract
def CPos(value):
  return value in range(1, 25) or value == HOME or value == BAR

@new_contract
def ValidateDice(dice):
    length_check = len(dice) == 2 or len(dice) == 4
    for die in dice:
        values_check = die in range(1, 7) 
    if len(dice) == 4:
        same_check = dice.count(dice[0]) == 4
        return length_check and values_check and same_check
    else:
        return length_check and values_check

@new_contract
def ValidateTurn(turn):
    for move in turn:
        if Color(move.color) and CPos(move.source_cpos) and CPos(move.dest_cpos):
            continue
        else: return False
    return True