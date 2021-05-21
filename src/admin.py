import backgammon as bg
from contracts.interface import ContractException, ContractNotRespected
from constants import *
from parse_data import get_moves_from_turn, create_moves
from contracts import new_contract, contract, check
import json, sys, socket

class BackgammonAdmin(object):
  @contract(config='dict', player1='dict', player2='dict')
  def __init__(self, config, player1=None, player2=None):
    self.config = config
    self.server = None
    self.winner = None
    self.board = bg.Board()
    self.dice = bg.Dice()
    if player1 and player2:
      self.init_game(player1, player2)
    else: self.init_game()

  # TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  @contract(player1='dict|None', player2='dict|None')
  def init_game(self, player1=None, player2=None):

    if self.config[LOCAL] == RANDO:
      self.player1 = bg.RandomPlayer(LOU)
    if self.config[LOCAL] == BOPSY:
      self.player1 = bg.BopPlayer(LOU)

    self.player1.color = self.board.get_color(bg.Black())
    self.current_player = self.player1

    # Setup remote player
    port = self.config[PORT]
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', port)
    self.socket.bind(server_address)
    self.socket.listen()

    msg = json.dumps('started')
    sys.stdout.flush()
    sys.stdout.write(msg)
    sys.stdout.flush()
    self.connection, client_address = self.socket.accept()
     
    msg = json.dumps(NAME)
    self.connection.sendall(msg.encode() + '\n'.encode())
    remote_name = json.loads(self.connection.recv(1024).decode())
    try:
      check('ValidateNameData', remote_name)
      name = remote_name[NAME]
      self.player2 = bg.RemotePlayer(name, port)
      self.player2.color = self.board.get_color(bg.White())

      #send start-game object
      self.connection.sendall(json.dumps({START: [self.player2.color.name(), self.player1.name]}).encode() + '\n'.encode())
      response = json.loads(self.connection.recv(1024).decode())

      while response:
        if response == OKAY: break
    except ContractNotRespected:
      self.ban_cheater()
    
    self.take_turns()

  def take_turns(self):
    while not self.board.finished():
      self.dice.roll() # roll new dice values at the beginning of each turn

      #local player turn
      if self.current_player == self.player1:
        self.current_player.turn(self.board, self.dice)

      #if remote player cheated and got replaced by Malnati
      elif self.current_player == self.player2 and not isinstance(self.player2, bg.RemotePlayer):
        self.current_player.turn(self.board, self.dice)

      #remote player turn 
      elif self.current_player == self.player2 and isinstance(self.player2, bg.RemotePlayer):
        # send message (take-turn json object), wait for response. if 'turn' object, validate moves and execute. if not 'turn' object
        # or if move is invalid, call ban_cheater and finish game with Malnati
        try:
          self.connection.sendall(json.dumps({TAKE_TURN: [self.board.as_dict(), self.dice.values]}).encode() + '\n'.encode())
          data = json.loads(self.connection.recv(1024).decode())
          check('ValidateTurnData', data)
          turn = data[TURN]
          get_moves_from_turn(turn, self.current_player.color)
          turn = create_moves(turn)
          if self.board.play_move(self.player2.color, self.dice, turn):
           pass
          else:
            self.ban_cheater() # ! if a player cheats, admin shuts down game and returns cheater (so tournament manager can edit bracket)
        except ContractNotRespected or ContractException:
          self.ban_cheater()
      else: raise ValueError('Something went wrong with player swapping')

      self._swap() # swap the players

    self.end_game()
    
    
  def ban_cheater(self):
    self.player2 = bg.RandomPlayer(MAL)
    self.player2.color = self.board.get_color(bg.White())
    self.connection.close()

  def end_game(self):
    local_has_won = self.player1.is_winner(self.board)
    remote_has_won = self.player2.is_winner(self.board)
    self.player1.end_game(self.board, local_has_won)
    if isinstance(self.player2, bg.RemotePlayer):
      self.connection.sendall(json.dumps({END: [self.board.as_dict(), remote_has_won]}).encode() + '\n'.encode())
      while True:
        msg = json.loads(self.connection.recv(1024).decode())
        if msg == OKAY: break
    else:
      self.player2.end_game(self.board, remote_has_won)

    if local_has_won:
      self.winner = self.player1
    if remote_has_won:
      self.winner = self.player2

    sys.stdout.write(json.dumps({WINNER: self.winner.name}) + '\n') #print admin-game-overb
    self.connection.close()

  def _swap(self):
    self.current_player = self.player1 if self.current_player != self.player1 else self.player2
