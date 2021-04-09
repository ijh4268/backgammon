import json
import sys
from sort_backend import sort

data = []
decoder = json.JSONDecoder()

for _ in range(0, 10):
  line = decoder.raw_decode(sys.stdin.readline())[0]
  data.append(line)

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))