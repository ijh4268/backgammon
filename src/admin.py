import backgammon as bg
from contracts.interface import ContractException, ContractNotRespected
from constants import *
from parse_data import get_moves_from_turn, create_moves
from contracts import new_contract, check
import json, sys, socket

@new_contract
def ValidateTurns(turns):
  if type(turns) == list:
    if len(turns) == 0: return True
    for turn in turns:
      if type(turn) == list:
        result = bg.CPos(turn[0]) and bg.CPos(turn[1])
      else: result = False
  else: result = False
  return result

@new_contract
def ValidateTurnData(data):
  return type(data) == dict and 'turn' in data.keys() and ValidateTurns(data['turn'])

@new_contract
def ValidateNameData(data):
  return type(data) == dict and 'name' in data.keys() and type(data['name']) == str

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

    self.local_player.color = self.board.get_color(bg.Black())
    self.current_player = self.local_player
    # self.ban_cheater()

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
     
    msg = json.dumps('name')
    self.connection.sendall(msg.encode() + '\n'.encode())
    remote_name = json.loads(self.connection.recv(1024).decode())
    try:
      check('ValidateNameData', remote_name)
      name = remote_name['name']
      self.remote_player = bg.RemotePlayer(name, port)
      self.remote_player.color = self.board.get_color(bg.White())

      #send start-game object
      self.connection.sendall(json.dumps({'start-game': [self.remote_player.color.name(), self.local_player.name]}).encode() + '\n'.encode())
      response = json.loads(self.connection.recv(1024).decode())

      while response:
        if response == 'okay': break
    except ContractNotRespected:
      self.ban_cheater()
    
    self.take_turns()

  def take_turns(self):
    while not self.board.finished():
      self.dice.roll() # roll new dice values at the beginning of each turn

      #local player turn
      if self.current_player == self.local_player:
        self.current_player.turn(self.board, self.dice)

      #if remote player cheated and got replaced by Malnati
      elif self.current_player == self.remote_player and not isinstance(self.remote_player, bg.RemotePlayer):
        self.current_player.turn(self.board, self.dice)

      #remote player turn 
      elif self.current_player == self.remote_player and isinstance(self.remote_player, bg.RemotePlayer):
        # send message (take-turn json object), wait for response. if 'turn' object, validate moves and execute. if not 'turn' object
        # or if move is invalid, call ban_cheater and finish game with Malnati
        try:
          self.connection.sendall(json.dumps({"take-turn": [self.board.as_dict(), self.dice.values]}).encode() + '\n'.encode())
          data = json.loads(self.connection.recv(1024).decode())
          check('ValidateTurnData', data)
          turn = data['turn']
          get_moves_from_turn(turn, self.current_player.color)
          turn = create_moves(turn)
          if self.board.play_move(self.remote_player.color, self.dice, turn):
           pass
          else:
            self.ban_cheater()
        except ContractNotRespected or ContractException:
          self.ban_cheater()
      else: raise ValueError('Something went wrong with player swapping')
      # Swap players
      # output = open("/Users/isaachenry/Projects/software_construction/src/log/7.1_boards.json", 'w')
      # json.dump([self.board.as_dict(),self.dice.values], output)
      self._swap()
    # output.close()
    self.end_game()
    
    
  def ban_cheater(self):
    self.remote_player = bg.RandomPlayer('Malnati')
    self.remote_player.color = self.board.get_color(bg.White())
    self.connection.close()

  def end_game(self):
    local_has_won = self.local_player.is_winner(self.board)
    remote_has_won = self.remote_player.is_winner(self.board)
    self.local_player.end_game(self.board, local_has_won)
    if isinstance(self.remote_player, bg.RemotePlayer):
      self.connection.sendall(json.dumps({"end-game": [self.board.as_dict(), remote_has_won]}).encode() + '\n'.encode())
      while True:
        msg = json.loads(self.connection.recv(1024).decode())
        if msg == "okay": break
    else:
      self.remote_player.end_game(self.board, remote_has_won)

    if local_has_won:
      self.winner = self.local_player
    if remote_has_won:
      self.winner = self.remote_player

    sys.stdout.write(json.dumps({"winner-name": self.winner.name}) + '\n') #print admin-game-overb
    self.connection.close()
    # self.__init__(self.config)

  def _swap(self):
    self.current_player = self.local_player if self.current_player != self.local_player else self.remote_player
