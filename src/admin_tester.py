from admin import BackgammonAdmin
from parse_json import parse_json
from constants import *

# parse json stuff
config = parse_json()[0]

# create instance of BackgammonAdmin
BackgammonAdmin(config)
