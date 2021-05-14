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

  #TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self):
    if self.config[LOCAL] == "Rando":
      local_player = bg.RandomPlayer('Lou')
    if self.config[LOCAL] == "Bopsy":
      local_player = bg.BopPlayer('Lou')

    # i think we're supposed to use our networking module here to initialize the remote player, but idk how
    port = self.config[PORT]
    try:
      self.server = initialize_network(port)
    except:
      # Do something here if there is an error
      pass

    print("started")
    remote_player = query_remote()
    remote_player.port = port

    def take_turns(self):
      pass
      # loop until an end_game object is received
      # if current player == local: use local_player.turn
      # elif current player == remote: use handle_turn
      # make sure to validate remote player's turns and call ban_cheater if invalid
      # advance turn

    def ban_cheater(self):
      self.server.close()
      remote_player = bg.RandomPlayer('Malnati')

    def end_game(self):
      local_player.end_game(self.board, local_player.check_winner())
      remote_player.end_game(self.board, remote_player.check_winner())
      #handle_end_game(self.server, data, remote_player) # still not sure where 'data' comes from
      self.server.close()

  #TODO: Ensure the remote player gets set up properly with the network and we get a response. Once a repsonse is received