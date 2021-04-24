import sys
import json
import re
from sort import sort

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

# only_dicts = parse_json()

# # Filter out any unwanted data
# filtered = list(filter(lambda x: len(x)==1 and special_feature in x \
#                         and type(x[special_feature]) == int \
#                         and x[special_feature] in valid_nums, only_dicts))

# # separate data into chuncks of 10
# chunks = list(chunkify(filtered, n))

# sorted = []
# for chunk in chunks:
#     if len(chunk) == n: sorted.append(sort(chunk, special_feature))

# sorted_json = json.dumps(sorted)


