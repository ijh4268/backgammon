from constants import *


def sort(array, special_feature):
  if special_feature == 'board':
    bars = list(filter(lambda x: x == BAR, array))
    homes = list(filter(lambda x: x == HOME, array))
    nums = list(sorted(filter(lambda x: type(x) == int, array)))
    return bars + nums + homes
  return sorted(array, key=lambda x: x[special_feature])