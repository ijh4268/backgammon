from math import log2

from contracts.interface import ContractNotRespected
from admin import BackgammonAdmin
from constants import *
import socket, sys, json, names
from contracts import new_contract, contract
import backgammon as bg
# Module to manage Backgammon tournaments
#------------------------------ Tournament Contracts -----------------------------
@new_contract
def ValidateNameData(data):
  return type(data) == dict and NAME in data.keys() and type(data[NAME]) == str and data[NAME].find('Filler') == -1

@new_contract
def Player(player):
  return isinstance(player, bg.Player)
#---------------------------------------------------------------------------------

class Tournament(object):
  def  __init__(self, config):
    self.players = []
    self.num_players = config[PLAYERS]
    self.num_connections = 0
    self.running = True
    self.get_remote_players('localhost', config[PORT])
    
    if config[TYPE] == ROUND_ROBIN:
      RoundRobin(config[PLAYERS], self.players)
      
    elif config[TYPE] == SINGLE_ELIM:
      SingleElim(config[PLAYERS], self.players)

  def get_remote_players(self, host, port):
    listener = socket.create_server((host, port), family=socket.AF_INET, backlog=self.num_players + 1)
    msg = json.dumps('started')
    sys.stdout.write(msg) # let the CI know the server has started 
    sys.stdout.flush()

    for i in range(self.num_players):
      client, _ = listener.accept()
      self.players.append(bg.RemotePlayer(client))
    listener.close()
    
  def _get_name_by_id(self, ident):
    for player in self.players:
      if player.ident == ident: return player.name
    raise Exception('id not found')

class RoundRobin(Tournament):
  def __init__(self, num_players, players):
    self.players = players
    self.num_players = num_players
    self.schedule = [] # probably want a list of tuples?
    self.cheaters = []
    self.match_history = {player.ident:[] for player in self.players}
    self.create_schedule()
    self.run_tournament()

  def create_schedule(self):                 
    for player in self.players:
      for opponent in self.players:
        if player.ident != opponent.ident and self.is_unique_matchup((player, opponent)):
          self.schedule.append((player, opponent))
  
  def handle_cheaters(self):
    for cheater in self.cheaters:
      wins = self.match_history[cheater.ident] # get players the cheater won against
      self.match_history[cheater.ident] = [] # clear the cheater's wins
      for player in wins:
        if not player.is_cheater: self.match_history[player.ident].append(cheater) # add the cheater to the wins for each player they won against
      
  def run_tournament(self):
    for match in self.schedule:
      player1 = match[0]
      player2 = match[1]

      admin = BackgammonAdmin(player1, player2)
      if admin.cheaters and admin.cheaters not in self.cheaters: self.cheaters = self.cheaters + admin.cheaters
      if not admin.winner: continue
      else: self.match_history[admin.winner.ident].append(admin.loser)
    self.end_tournament()

  def end_tournament(self):
    self.handle_cheaters()
    for player in self.players:
      if isinstance(player, bg.RemotePlayer):
        player.client.close()

    results = self.get_results()
    # return the winners with wins and losses
    sys.stdout.write(json.dumps(results))
  
  def get_results(self):
    results = []
    for playerid in self.match_history:
      wins = len(self.match_history[playerid])
      potential_losses = (self.num_players - 1) - wins
      losses = potential_losses if potential_losses >= 0 else 0
      results.append([self._get_name_by_id(playerid), wins, losses])
    # sort the results by number of wins
    results.sort(key=lambda x: x[1], reverse=True)
    return results
    
  def is_unique_matchup(self, matchup):
    reverse = (matchup[1], matchup[0])
    if matchup in self.schedule:
        return False
    elif reverse in self.schedule:
        return False
    else: return True

class SingleElim(Tournament):
  @contract(num_players='int', players='list(Player)')
  def __init__(self, num_players, players):
    self.num_players = num_players
    self.players = players
    self.bracket = []
    self.waiting_room = self.players

    self.create_bracket()
    self.run_tournament()

  def create_bracket(self):
    num_fillers = 0
    while not log2(self.num_players + num_fillers).is_integer():
      num_fillers += 1
      filler = bg.RandomPlayer("Filler " + names.get_first_name())
      self.players.append(filler)
      self.waiting_room = self.players  

    self.new_matchups()

  def run_tournament(self):
    while self.bracket and len(self.waiting_room) != 1:
      for matchup in self.bracket: #loop until final matchup
        player1 = matchup[0]
        player2 = matchup[1]

        admin = BackgammonAdmin(player1, player2)
        self.advance_winner(admin.winner)
      
      self.new_matchups()
    self.end_tournament()

  def end_tournament(self):
    for player in self.players:
      if isinstance(player, bg.RemotePlayer):
        player.client.close()

    if "Filler" in self.waiting_room[0].name or self.waiting_room[0].is_cheater:
      sys.stdout.write(json.dumps(False))
    else:
      sys.stdout.write(json.dumps(self.waiting_room[0].name))

  def advance_winner(self, winner):
    self.waiting_room.append(winner)
    
  def new_matchups(self):
    if len(self.waiting_room) >= 2 and len(self.waiting_room) % 2 == 0:
      self.bracket = list(zip(*(iter(self.waiting_room),) * 2))
      self.waiting_room = []