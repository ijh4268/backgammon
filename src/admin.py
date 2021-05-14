import backgammon as bg

# HELLO THIS IS A TEST

class BackgammonAdmin(object):
  def __init__(self):
    pass

  #TODO: Initialize Game func (takes in the admin config and sets up the two Players)
  def init_game(self, config):
    if config['local'] == "Rando":
      local_player = bg.RandomPlayer('Lou')
    if config['local'] == "Bopsy":
      local_player = bg.BopPlayer('Lou')

    # i think we're supposed to use our networking module here to initialize the remote player, but idk how
    remote_player = bg.Player('')

    def ban_cheater(self):
      pass

    def end_game(self):
      pass

  #TODO: Ensure the remote player gets set up properly with the network and we get a response. Once a repsonse is received