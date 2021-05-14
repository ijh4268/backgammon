from admin import BackgammonAdmin
from parse_json import parse_json
from constants import *
import json
import sys

# parse json stuff
data = parse_json()[0]
config = dict(filter(lambda x: x[0] == LOCAL or x[0] == PORT, data.items()))

# create instance of BackgammonAdmin
admin = BackgammonAdmin(config)

# Play some games