import socket
import sys
import json
from backgammon import RandomPlayer
from parse_json import parse_json
from constants import *

# Take the JSON object 'network-config' and extract the "host" (string, goes to TCP_IP) and the "port" (number, goes to TCP_PORT)
network_config = json.loads(sys.stdin.readline())

TCP_IP = network_config[HOST]
TCP_PORT = network_config[PORT]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(TCP_IP)

s.connect((host, TCP_PORT))

name = s.recv(1024)
player = RandomPlayer(name)
s.sendall(player.name.encode())

start_game = s.recv(1024)
take_turn = s.recv(1024)
end_game = s.recv(1024)

print(name.decode())
print(start_game.decode())
print(take_turn.decode())
print(end_game.decode())

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