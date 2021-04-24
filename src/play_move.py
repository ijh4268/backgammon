from constants import *


#------------ WRITE A NEW METHOD FOR BOARD THAT PLAYS A SINGLE MOVE -------------
def play_move(board, color, turn):
    for move in turn:
        if color == BLACK:
            posns = board.black_posns
        if color == WHITE:
            posns = board.white_posns
        src = move.source_cpos
        dst = move.dest_cpos
        occupants = color_check(dst)

        # If there is no checker at src, then the move is invalid
        if src_exists(board, move) == True:
            # If a player has checkers on the bar, that takes first priority
            if BAR in posns:
                if occupants == color or occupants == None:
                    board.make_moves(move)
                if occupants != color:
                    return False
        
            # You can move checkers to points that are occupied by your own color (with no maximum limit of checkers on one point)
            if occupants == color or occupants == None:
                board.make_moves(move)
            
            # If your opponent only has one checker at the dst position, then the move is a 'bop'. Your piece takes the position and their piece is sent to the bar.
            if occupants != turn and is_bop(dst) == True:
                board.make_moves(move)
                board.bop() # THIS IS NOT AN ACTUAL FUNCTION
        else:
            return False

    return board


#---------------------- HELPER FUNCTIONS ----------------------

# Checks if there is a checker in the src position (given by the Move object)
def src_exists(board, move):
    color = color_check(board, move.source_cpos)
    if color == move.color:
        return True
    else:
        return False

# Checks what color is currently occupying the given dst position
def color_check (board, pos):
    if pos in board.black_posns:
      return BLACK
    if pos in board.white_posns:
      return WHITE
    else: 
      return None

# Checks how many pieces are occupying a given dst position (helper function for is_bop)
def num_pc(board, pos):
    if color_check(board, pos) == BLACK:
        return board.black_posns.count(pos)
    if color_check(board, pos) == WHITE:
        return board.white_posns.count(pos)
    else:
        return 0

# Checks if the move is a bop
def is_bop(board, move):
    if color_check(move.dest_cpos) != move.color and num_pc(board, move.dest_cpos) == 1:
        return True
    else:
        return False

# Advances the turn and changes the color to the current player's color
def advance(curr):
    if curr == BLACK:
        return WHITE
    if curr == WHITE: 
        return BLACK

'''
def __init__(self):
    self.values = [randint(1,6), randint(1,6)]
    if self.values[0] == self.values[1]:
        self.values.append(self.values[0])
        self.values.append(self.values[0])
'''