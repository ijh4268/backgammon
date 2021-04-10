import json
import sys
import re
from sort_backend import sort

data = []

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
            # do something sensible if there's some error
            raise
        yield obj

s = sys.stdin.read().strip('[]\n')

for item in decode_stacked(s):
  data.append(item)

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))