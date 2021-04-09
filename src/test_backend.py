import json
import sys
from sort_backend import sort

data = []

for line in sys.stdin:
  try: 
    line_data = json.loads(line)
  except json.JSONDecodeError:
    exit(0)
  data.append(json.loads(line))

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))