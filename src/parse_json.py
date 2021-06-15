import sys
import json
import re

data = []
n = 10 
valid_nums = range(1, 25)
special_feature = 'content'

NOT_WHITESPACE = re.compile(r'[^\s]')

def decode_stacked(document, pos=0, decoder=json.JSONDecoder()):
    while True:
        match = NOT_WHITESPACE.search(document, pos)
        if not match:
            return
        pos = match.start()
        
        try:
            obj, pos = decoder.raw_decode(document, pos)
        except json.JSONDecodeError:
            pass
        yield obj

def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def parse_json():
    s = sys.stdin.read()
    # Add JSON data to a list of all data
    for item in decode_stacked(s):
        data.append(item)
    only_dicts = list(filter(lambda x: type(x) == dict or type(x) == list, data))
    return only_dicts
