import json
import sys
from sort_backend import sort

data = []

for line in sys.stdin:
  try: 
    line_data = json.loads(line)
  except json.JSONDecodeError:
    pass
  data.append(json.loads(line))

for dict in data:
  k, v = dict.items()
  if k != "content" or type(v) is not int or v not in range(1, 25):
    del dict

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))