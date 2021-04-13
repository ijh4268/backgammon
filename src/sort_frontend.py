import sys
import json
import re
from sort_backend import sort

data = []
n = 10 
valid_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

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

s = sys.stdin.read()
# Add JSON data to a list of all data
for item in decode_stacked(s):
    data.append(item)

only_dicts = list(filter(lambda x: type(x) == dict, data))

# Filter out any unwanted data
filtered = list(filter(lambda x: len(x)==1 and "content" in x \
                        and type(x['content']) == int \
                        and x['content'] in valid_nums, only_dicts))

# separate data into chuncks of 10
chunks = list(chunkify(filtered, n))

sorted = []
for chunk in chunks:
    if len(chunk) == n: sorted.append(sort(chunk))

sorted_json = json.dumps(sorted)

sys.stdout.flush()
sys.stdout.write(sorted_json)
