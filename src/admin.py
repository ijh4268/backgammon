import backgammon as bg
from networking import *
from constants import *

class BackgammonAdmin(object):
  def __init__(self, config):
    self.config = config
    self.server = None
    self.winner = None
    self.board = bg.Board()
    self.curr_turn = None
    self.init_game()

  #TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self):
    if self.config[LOCAL] == "Rando":
      self.local_player = bg.RandomPlayer('Lou')
    if self.config[LOCAL] == "Bopsy":
      self.local_player = bg.BopPlayer('Lou')

    # Setup remote player
    port = self.config[PORT]
    try:
      self.server = initialize_network(port)
    except:
      # Do something here if there is an error
      pass

    self.remote_player = query_remote()
    self.remote_player.port = port

    def take_turns(self):
      while not self.board.finished():
        self.current_player.turn()
      

    def ban_cheater(self):
      self.server.close()
      self.remote_player = bg.RandomPlayer('Malnati')

    def end_game(self):
      self.local_player.end_game(self.board, self.local_player.check_winner())
      self.remote_player.end_game(self.board, self.remote_player.check_winner())
      #handle_end_game(self.server, data, remote_player) # still not sure where 'data' comes from
      self.server.close()

  #TODO: Ensure the remote player gets set up properly with the network and we get a response. Once a repsonse is received