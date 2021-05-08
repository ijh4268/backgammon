from constants import *
import backgammon as bg
from parse_data import get_board, get_dice
import socket
import sys
import json

# Take the JSON object 'network-config' and extract the "host" (string, goes to TCP_IP) and the "port" (number, goes to TCP_PORT)
network_config = json.loads(sys.stdin.readline())

TCP_IP = network_config[HOST]
TCP_PORT = network_config[PORT]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(TCP_IP)

s.connect((host, TCP_PORT))

while True:
  data = json.loads(s.recv(1024).decode())
  if data == 'name':
    player = bg.RandomPlayer(data)
    player_name_json = json.dumps({'name': player.name})
    s.send(player_name_json.encode())
  elif type(data) == dict and 'start-game' in data.keys():
    start_game = data['start-game']
    color = start_game[0]
    opponent = start_game[1]
    try:
      player.start_game(color, opponent)
      assert player.color == color
      assert player.opponent == opponent
      s.send(json.dumps('okay').encode())
    except AssertionError as e:
      raise e
  elif type(data) == dict and 'take-turn' in data.keys():
    turn = data['take-turn']
    board = get_board(turn[0])
    dice = get_dice(turn[1])
    result = player.turn(board, dice)
    s.send(json.dumps(result).encode())
  elif type(data) == dict and 'end-game' in data.keys():
    end_game = data['end-game']
    final_board = get_board(end_game[0])
    has_won = end_game[1]
    try:
      player.end_game(final_board, has_won)
      assert player.final_board == final_board
      assert player.has_won == has_won
      s.send(json.dumps('okay').encode())
    except AssertionError as e:
      raise e

s.close()
# if data == "name":
#     print(player.name) # idk how the player class fits into here, i guess we have to adjust the class and methods in backgammon.py
# elif 'start-game' in data:
#     player.start_game
#     print("Please confirm by saying 'okay': ") 
#     # have player type "okay" here.. are we supposed to check if the player responds with "okay" or do we just assume they will?

# elif 'take-turn' in data:
#     player.turn
#     print("Please give a list of moves you would like to take: ")
#     # have player give a 'turn' object (must be valid with the given dice values).. again, do we have to check here if the list of moves is valid, or if the player even gave a list of moves

# elif 'end-game' in data:
#     player.end_game
#     print("Please confirm by saying 'okay': ")
#     # have player type "okay" here