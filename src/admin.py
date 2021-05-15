import backgammon as bg
from networking import *
from constants import *

class BackgammonAdmin(object):
  def __init__(self, config):
    self.config = config
    self.server = None
    self.winner = None
    self.board = bg.Board()
    self.current_player = None
    self.init_game()

  #TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self):
    self.dice = bg.Dice([0, 0])

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

    print("started") #print admin-networking-started


    def take_turns(self):
      while not self.board.finished():
        self.dice.roll() # roll new dice values at the beginning of each turn
        self.current_player.turn()

        #local player turn
        if self.current_player == self.local_player:
          # generate valid moves with the current board, use _get_move to get a move, then execute move on self.board
          pass

        #remote player turn
        if self.current_player == self.remote_player:
          # send message (take-turn json object), wait for response. if 'turn' object, validate moves and execute. if not 'turn' object
          # or if move is invalid, call ban_cheater and finish game with Malnati
          pass

        self.current_player = self.current_player.opponent # advance the turn at the end of each turn
      

    def ban_cheater(self):
      self.server.close()
      self.remote_player = bg.RandomPlayer('Malnati')


    def end_game(self):
      self.local_player.end_game(self.board, self.local_player.check_winner())
      #self.remote_player.end_game(self.board, self.remote_player.check_winner()) //// should be sending end-game object through server

      # check who's the winner and set in self.winner
      if self.local_player.check_winner() == True:
        self.winner = self.local_player
      if self.remote_player.check_winner() == True:
        self.winner = self.remote_player
      else:
        #raise some error because there is no winner D: (is this check even necessary?)
        pass 

      admin_game_over = {"winner-name": self.winner.name}
      print(json.dumps(admin_game_over)) #print admin-game-over
      self.server.close()

  #TODO: Ensure the remote player gets set up properly with the network and we get a response. Once a repsonse is received