import backgammon as bg
from contracts.interface import ContractException, ContractNotRespected
from constants import *
from parse_data import get_moves_from_turn, create_moves
from contracts import new_contract, contract, check

# @new_contract
# def Player(player):
#   return isinstance(player, bg.Player)

class BackgammonAdmin(object):
  def __init__(self, player1=None, player2=None):
    self.winner = None
    self.loser = None
    self.cheater = None
    self.board = bg.Board()
    self.dice = bg.Dice()
    self.player1 = player1
    self.player2 = player2
    self.init_game(player1, player2)

  def cheater_check(self):
    if self.player1.is_cheater and self.player2.is_cheater:
      self.cheater = -1
    elif self.player1.is_cheater:
      self.cheater = [self.player1]
    elif self.player2.is_cheater:
      self.cheater = [self.player2]
    else: return 


  # TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self, player1=None, player2=None):

    self.current_player = self.player1

    self.player1.color = self.board.get_color(bg.Black())
    self.player2.color = self.board.get_color(bg.White())
    #send start-game object
    self.player1.start_game(self.player1.color.name(), self.player2.name)
    self.player2.start_game(self.player2.color.name(), self.player2.name)


    self.cheater_check()

    self.take_turns()

  def take_turns(self):
    while not self.board.finished() and not self.cheater:
      self.dice.roll() # roll new dice values at the beginning of each turn

      #local player turn
      self.current_player.turn(self.board, self.dice)

      self._swap() # swap the players

    self.end_game()
    
  def end_game(self):

    if self.cheater:
      if self.player1 in self.cheater:
        p1_has_won = False
        p2_has_won = True
        self.player2.end_game(self.board, p2_has_won)
      elif self.player2 in self.cheater:
        p1_has_won = True
        p2_has_won = False
        self.player1.end_game(self.board, p1_has_won)
    else:
      p1_has_won = self.player1.is_winner(self.board) 
      p2_has_won = self.player2.is_winner(self.board) 
      self.player1.end_game(self.board, p1_has_won)
      self.player2.end_game(self.board, p2_has_won)

    self.cheater_check()

    if self.cheater == -1:
      p1_has_won = False
      p2_has_won = False
      self.cheater = [self.player1, self.player2]
      
    if p1_has_won:
      self.winner = self.player1
      self.loser = self.player2 
    elif p2_has_won:
      self.winner = self.player2
      self.loser = self.player1
    else:
      self.winner = False
    
  def _swap(self):
    self.current_player = self.player1 if self.current_player != self.player1 else self.player2
