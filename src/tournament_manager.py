from math import log2

from contracts.interface import ContractNotRespected
from admin import BackgammonAdmin
from constants import *
import socket, sys, json, names
from threading import Thread
from contracts import new_contract, check, contract, disable_all
import backgammon as bg
# Module to manage Backgammon tournaments
#---------------------------- Tournament Contracts ---------------------------
disable_all()
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

class RoundRobin(object):
  def __init__(self, num_players, players):
    self.players = players
    self.num_players = num_players
    self.schedule = [] # probably want a list of tuples?
    self.match_history = {player.ident:[] for player in self.players}
    self.results = []
    self.run_tournament()

  def create_schedule(self):
    for player in self.players:
        for opponent in self.players:
            if player != opponent and self.is_unique_matchup((player, opponent)):
                self.schedule.append((player, opponent))
  
  @contract(cheater='Player')
  def handle_cheaters(self, cheater):
    for cheater in cheater:
      for player in self.match_history[cheater.ident]:
        self.match_history[player.ident].append(cheater.ident)
      self.match_history[cheater.ident] = []
      
  def run_tournament(self):
    for match in self.schedule:
      player1 = match[0]
      player2 = match[1]

      admin = BackgammonAdmin(player1, player2)
      if admin.cheater: self.handle_cheaters(admin.cheater)
      if not admin.winner: continue
      else: self.match_history[admin.winner.ident].append(admin.loser.ident)
  
  def end_tournament(self):
    for player in self.players:
      if isinstance(player, bg.RemotePlayer):
        player.client.close()

    for playerid in self.match_history:
      wins = len(self.match_history[playerid])
      losses = (self.num_players - 1) - wins
      self.results.append([self._get_name_by_id(playerid), wins, losses])
    # sort the results by number of wins
    self.results.sort(key=lambda x: x[1], reverse=True)
    # return the winners with wins and losses
    sys.stdout.write(json.dumps(self.results))
  
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
    self.bracket = []
    self.waiting_room = self.players

    self.create_bracket()
    self.run_tournament()

  def create_bracket(self):
    while not log2(self.num_players + self.num_fillers).is_integer() \
      or log2(self.num_players + self.num_fillers) == 0:
      self.num_fillers += 1
      filler = bg.RandomPlayer("Filler " + names.get_first_name())
      self.players.append(filler)
      self.waiting_room = self.players

    self.new_matchups()

  def run_tournament(self):
    while self.bracket: #loop until final matchup
      for matchup in self.bracket:
        # filler vs filler
        # if "Filler" in matchup[0].name and "Filler" in matchup[1].name:
        #   admin = BackgammonAdmin()
        #   self.advance_winner(matchup, matchup[0])
        player1 = matchup[0]
        player2 = matchup[1]
        # else:
        admin = BackgammonAdmin(player1, player2)
        self.advance_winner(matchup, admin.winner)
      
      if len(self.waiting_room) == 1: break # end tournament when only one player left in bracket (not to be confused with one matchup left)
      
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

  def advance_winner(self, matchup, winner):
    self.bracket.remove(matchup)
    self.waiting_room.append(winner)
    
  def new_matchups(self):    
    while self.waiting_room:
      matchup = [self.waiting_room.pop(), self.waiting_room.pop()]
      self.bracket.append(matchup)
    
  #* if this doesn't work, then we can add a new attribute "waiting_room" to hold the individual players after they win their match
  #* this means bracket will hold purely matchups and "waiting_room" will hold purely individuals
  #* then make a new bracket with contents of waiting_room