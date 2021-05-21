from math import log2

from contracts.interface import ContractNotRespected
from admin import BackgammonAdmin
from constants import *
import socket, sys, json, names
from threading import Thread
from contracts import new_contract, check, contract
import backgammon as bg
# Module to manage Backgammon tournaments
#---------------------------- Tournament Contracts ---------------------------
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
  return type(data) == dict and TURN in data.keys() and ValidateTurns(data[TURN])

@new_contract
def ValidateNameData(data):
  return type(data) == dict and NAME in data.keys() and type(data[NAME]) == str and data[NAME].find('Filler') == -1

@new_contract
def Player(player):
  return isinstance(player, bg.Player)
#---------------------------------------------------------------------------------

class Tournament(object):
  def  __init__(self, config):
    # ? I think for scheduling, we should have a list of players to iterate through? Maybe
    self.players = []
    self.socket = socket.socket()
    self.running = True
    self.init_server(config[PORT])
    
    if config[TYPE] == ROUND_ROBIN:
      self.tourney = RoundRobin(config[PLAYERS], self.players)
    
    elif config[TYPE] == SINGLE_ELIM:
      self.tourney = SingleElim(config[PLAYERS], self.players)

  
  # set up the server given the tourny config
  def on_new_client(self, client, address):
    # get the name of the player
    try:
      msg = json.dumps('name')
      client.send(msg.encode() + '\n'.encode())
      data = client.recv(1024).decode()
      check('ValidateNameData', data)
      name = data[NAME]
      self.players.append(bg.RemotePlayer(name, client, address))
    except ContractNotRespected:
      # ! do something if the name is invalid
      # // we should make sure the remote player can't choose a name with "Filler" in it
      client.close()

  def init_server(self, port):
    host = self.socket.gethostname()
    self.socket.bind((host, port))
    self.socket.listen(5)
    sys.stdout.flush()
    sys.stdout.write('started') # let the CI know the server has started 
    while self.running:
      num_connections = 0
      while num_connections < self.num_players:
        client, address = self.socket.accept()
        Thread(target=self.on_new_client, args=(client))
        num_connections += 1
    self.socket.close()

  # branch off the the given tournament type (rr or se)
  


class RoundRobin(object):
  def __init__(self, num_players, players):
    self.players = players
    self.num_players = num_players
    self.schedule = [] # probably want a list of tuples?
    self.match_history = {player.name:[] for player in self.players}
    self.results = []

  #TODO: scheduling algorithm 
  def create_schedule(self):
    for player in self.players:
        for opponent in self.players:
            if player != opponent and self.is_unique_matchup([player, opponent]):
                self.schedule.append([player, opponent])
  
  @contract(cheater='Player')
  def handle_cheaters(self, cheater):
    for player in self.match_history[cheater.name]:
      self.match_history[player.name].append(cheater.name)
    self.match_history[cheater.name] = []

  def run_tournament(self):
    pass
  
  def end_tournament(self):
    for player in self.match_history:
      wins = len(self.match_history[player])
      losses = (self.num_players - 1) - wins
      self.results.append([player, wins, losses])
    # sort the results by number of wins
    self.results.sort(key=lambda x: x[1], reverse=True)
    # return the winners with wins and losses
  
  def is_unique_matchup(self, matchup):
    reverse = [matchup[1], matchup[0]]
    if matchup in self.schedule:
        return False
    elif reverse in self.schedule:
        return False
    else: return True


class SingleElim(object):
  @contract(num_players='int', players='list(Player)')
  def __init__(self, num_players, players):
    self.num_players = num_players
    self.num_fillers = 0
    self.players = players
    self.bracket = self.players

    self.create_bracket()
    self.run_tournament()

  def create_bracket(self):
    while type(log2(self.num_players)) is not int:
      self.num_fillers += 1
      filler = bg.RandomPlayer("Filler " + names.get_first_name())
      self.players.append(filler)

    self.new_matchups()

  def run_tournament(self):
    admin = None # TODO: create admin instance
    while len(self.bracket) >= 1: #loop until final match
      bracket_copy = self.bracket
      for matchup in bracket_copy:
        # real player vs real player
        # TODO: initialize admin with two players in matchup
        if admin.take_turns() is Player(): #! checking if admin.take_turns() returns a player (aka cheater)
          self.advance_winner(matchup, admin.take_turns().opponent)
        else:
          self.advance_winner(matchup, admin.winner)
          admin.reset()

        # real player vs filler
        # TODO: initialize admin with player in matchup + filler
        if admin.take_turns() is Player(): #! checking if admin.take_turns() returns a player (aka cheater)
          self.advance_winner(matchup, admin.take_turns().opponent)
        else:
          self.advance_winner(matchup, admin.winner)
          admin.reset()     

        # filler vs filler
        if "Filler" in matchup[0].name and "Filler" in matchup[1].name:
          self.advance_winner(matchup, matchup[0])
      
      if len(self.bracket) == 1: break # end tournament when only one player left in bracket
      
      self.new_matchups()
    self.end_tournament()

  # end tournament method: return name of winning player (or False if filler wins - god-forbid)
  def end_tournament(self):
    if "Filler" in self.bracket[0].name:
      sys.stdout.write(json.dumps(False) + '\n')
    else:
      sys.stdout.write(json.dumps(self.bracket[0].name) + '\n')

  def advance_winner(self, matchup, winner):
    self.bracket.remove(matchup)
    self.bracket.append(winner)
    
  def new_matchups(self):
    count = 0
    while count <= self.bracket.len():
      matchup = [self.bracket[count], self.bracket[count+1]]
      matchup[0].opponent = matchup[1] # * not sure if the opponent will be initialized by admin; if admin does, remove this line..
      matchup[1].opponent = matchup[0] # * ..and this one
      self.bracket.remove(self.bracket[count])
      self.bracket.remove(self.bracket[count+1])
      self.bracket.append(matchup)
      count += 2