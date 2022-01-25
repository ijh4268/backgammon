import backgammon as bg
import socket
import json
import sys
from admin import BackgammonAdmin
from constants import *
from parse_json import parse_json

def get_remote_player(host, port):
  listener = socket.create_server((host, port), family=socket.AF_INET, backlog=1)
  msg = json.dumps('started')
  sys.stdout.write(msg)  # let the CI know the server has started
  sys.stdout.flush()

  client, _ = listener.accept()
  remote_player = bg.RemotePlayer(client)
  listener.close()
  return remote_player

# parse json stuff
config = parse_json()[0]

# create instance of BackgammonAdmin
if config['local'] == 'Rando':
  local_player = bg.RandomPlayer(LOU)
elif config['local'] == 'Bopsy':
  local_player = bg.AIPlayer(LOU)
else:
  raise ValueError('Incorrect config')
  
remote_player = get_remote_player('localhost', config[PORT])

admin = BackgammonAdmin(local_player, remote_player, testing=True)

winner = json.dumps({'winner-name': admin.winner.name})
sys.stdout.write(winner)

