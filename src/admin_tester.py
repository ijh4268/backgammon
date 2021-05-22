from admin import BackgammonAdmin
from parse_json import parse_json


# parse json stuff
config = parse_json()[0]

# create instance of BackgammonAdmin
BackgammonAdmin(config)
