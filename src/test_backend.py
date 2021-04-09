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

for item in data:
  if item.key != "content" or type(item.value) is not int:
    del item

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))