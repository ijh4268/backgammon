from contracts.interface import ContractNotRespected
import backgammon as bg
import socket
from constants import *
import json
import sys

class BackgammonAdmin(object):
  def __init__(self, config):
    self.config = config
    self.server = None
    self.winner = None
    self.board = bg.Board()
    self.dice = bg.Dice()
    self.init_game()

  # TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self):

    if self.config[LOCAL] == 'Rando':
      self.local_player = bg.RandomPlayer('Lou')
    if self.config[LOCAL] == 'Bopsy':
      self.local_player = bg.BopPlayer('Lou')

    self.local_player.color = bg.Black()
    self.current_player = self.local_player

    # Setup remote player
    port = self.config[PORT]
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    self.socket.bind(server_address)
    self.socket.listen(port)
      
    msg = json.dumps({'admin-networking-started': 'started'})
    sys.stdout.write(msg)
      
    while True:
      self.connection, client_address = self.socket.accept()
  
      try:
        self.connection.send(json.dumps('name').encode())
        remote_name = json.loads(self.connection.recv(1024).decode())
        self.remote_player = bg.RemotePlayer(remote_name)
        self.remote_player.color = bg.White()

        #send start-game object
        self.connection.send(json.dumps({'start-game': [self.remote_player.color.name(), self.local_player.name]}).encode())
        response = json.loads(self.connection.recv(1024).decode())

        while response:
          if response == 'okay': break
      
        self.take_turns()
      except:
        pass


  def take_turns(self):
    while not self.board.finished():
      self.dice.roll() # roll new dice values at the beginning of each turn

      #local player turn
      if self.current_player == self.local_player:
        self.current_player.turn(self.board, self.dice)

      #if remote player cheated and got replaced by Malnati
      if self.current_player == self.remote_player and self.remote_player.is_remote == False:
        self.current_player.turn(self.board, self.dice)

      #remote player turn 
      if self.current_player == self.remote_player and self.remote_player.is_remote == True:
        # send message (take-turn json object), wait for response. if 'turn' object, validate moves and execute. if not 'turn' object
        # or if move is invalid, call ban_cheater and finish game with Malnati
        self.connection.send(json.dumps({"take-turn": [self.board, self.dice]}).encode())
        turn = json.loads(self.connection.recv(1024).decode())
        try:
          if self.board.play_move(self.remote_player.color, self.dice, turn) == False:
            self.ban_cheater()
          else:
            self.board.play_move(self.remote_player.color, self.dice, turn)
        except ContractNotRespected:
          self.ban_cheater()

      self.current_player = self.current_player.opponent # advances the turn at the end of each turn
    self.end_game()
    

  def ban_cheater(self):
    self.connection.close()
    self.remote_player = bg.RandomPlayer('Malnati')
    self.remote_player.is_remote = False


  def end_game(self):
    local_has_won = self.local_player.is_winner()
    remote_has_won = self.remote_player.is_winner()
    self.local_player.end_game(self.board, local_has_won)
    self.connection.send(json.dumps({"end-game": [self.board, remote_has_won]}))
    while True:
      msg = json.loads(self.connection.recv(1024).decode())
      if msg == "okay": break

    if local_has_won:
      self.winner = self.local_player
    if remote_has_won:
      self.winner = self.remote_player
    else:
      #raise some error because there is no winner D: (is this check even necessary?)
      pass 

    print(json.dumps({"winner-name": self.winner.name})) #print admin-game-over
    self.connection.send(json.dumps({"winner-name": self.winner.name}).encode())
    self.connection.close()
    self.__init__(self.config)
