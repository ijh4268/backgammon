from constants import *
import backgammon as bg
from parse_data import get_board, get_dice, get_color
import socket
import sys
import json

# Take the JSON object 'network-config' and extract the "host" (string, goes to TCP_IP) and the "port" (number, goes to TCP_PORT)
# network_config = json.loads(sys.stdin.readline())

# port = network_config[PORT]

def initialize_network(port, host='localhost', is_admin=True):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostbyname(host)
  s.connect((host, port))
  if is_admin:
    confirmation = json.dumps({'admin-networking-started': 'started'})
    s.send(confirmation.encode() + '\n'.encode())
  return s

# s = initialize_network(port, is_admin=False)

def handle_name(server, data):
  player = bg.RemotePlayer(data)
  player_name_json = json.dumps({'name': player.name})
  server.send(player_name_json.encode() + '\n'.encode())
  return player

def handle_start_game(server, data, player):
  start_game = data['start-game']
  color = start_game[0]
  opponent = start_game[1]
  try:
    player.start_game(color, opponent)
    assert player.color == color
    assert player.opponent == opponent
    server.send(json.dumps('okay').encode() + '\n'.encode())
  except AssertionError as e:
    raise e

def handle_turn(server, data, player):
  turn = data['take-turn']
  board = get_board(turn[0])
  player.color = get_color(player.color, board)
  dice = get_dice(turn[1])
  result = player.turn(board, dice)
  server.send(json.dumps({'turn': result}).encode() + '\n'.encode())

def handle_end_game(server, data, player):
  end_game = data['end-game']
  final_board = get_board(end_game[0])
  has_won = end_game[1]
  try:
    player.end_game(final_board, has_won)
    assert player.final_board == final_board
    assert player.has_won == has_won
    server.send(json.dumps('okay').encode() + '\n'.encode())
  except AssertionError as e:
    raise e

def query_remote():
  data = json.loads(s.recv(1024).decode())
  while data:
    if data == 'name':
      player = handle_name(s, data)
    elif type(data) == dict and 'start-game' in data.keys():
      handle_start_game(s, data, player)
    elif type(data) == dict and 'take-turn' in data.keys():
      handle_turn(s, data, player)
    elif type(data) == dict and 'end-game' in data.keys():
      handle_end_game(s, data, player)
    data = json.loads(s.recv(1024).decode())