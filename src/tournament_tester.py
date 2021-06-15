from tournament_manager import Tournament
from parse_json import parse_json

config = parse_json()[0]

Tournament(config)
