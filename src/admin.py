import random
import backgammon as bg
from constants import *


# @new_contract
# def Player(player):
#   return isinstance(player, bg.Player)

class BackgammonAdmin(object):
  def __init__(self, player1=None, player2=None):
    self.winner = None
    self.loser = None
    self.cheaters = None
    self.board = bg.Board()
    self.dice = bg.Dice()
    self.player1 = player1
    self.player2 = player2
    self.init_game()

  def cheater_check(self):
    if self.player1.is_cheater and self.player2.is_cheater:
      self.cheaters = -1
    elif self.player1.is_cheater:
      self.cheaters = [self.player1]
    elif self.player2.is_cheater:
      self.cheaters = [self.player2]
    else: return 

  def check_fillers(self):
    return 'Filler' in self.player1.name and 'Filler' in self.player2.name

  def init_game(self):
    self.current_player = self.player1

    try:
      if self.check_fillers():
        raise Exception

      self.player1.color = bg.Black()
      self.player2.color = bg.White()
      #send start-game object
      if self.player1.is_cheater: 
        self.player2.start_game(self.player2.color.name(), self.player1.name)
      elif self.player2.is_cheater:
        self.player1.start_game(self.player1.color.name(), self.player2.name)
      else:
        self.player1.start_game(self.player1.color.name(), self.player2.name)
        self.player2.start_game(self.player2.color.name(), self.player1.name)

      self.cheater_check()

      self.take_turns()
    except Exception:
      # both players are fillers, choose winner by coin toss
      self.handle_fillers()

  def take_turns(self):
    while not self.board.finished() and not self.cheaters:
      self.dice.roll() # roll new dice values at the beginning of each turn

      #local player turn
      self.current_player.turn(self.board, self.dice)

      self.cheater_check()

      self._swap() # swap the players

    self.end_game()
    
  def end_game(self):

    if self.cheaters:
      if self.player1 in self.cheaters:
        p1_has_won = False
        p2_has_won = True
        self.player2.end_game(self.board, p2_has_won)
      elif self.player2 in self.cheaters:
        p1_has_won = True
        p2_has_won = False
        self.player1.end_game(self.board, p1_has_won)
    else:
      p1_has_won = self.player1.is_winner(self.board) 
      p2_has_won = self.player2.is_winner(self.board) 
      self.player1.end_game(self.board, p1_has_won)
      self.player2.end_game(self.board, p2_has_won)

    self.cheater_check()

    if self.cheaters == -1:
      p1_has_won = False
      p2_has_won = False
      self.cheaters = [self.player1, self.player2]
      
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

  def handle_fillers(self):
    fillers = [self.player1, self.player2]
    self.winner = random.choice(fillers)
    fillers.remove(self.winner)
    self.loser = fillers[0]
  