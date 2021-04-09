import json
import sys
from sort_backend import sort

data = []

for line in sys.stdin:
  try: 
    line_data = json.loads(line)
  except:
    pass
  data.append(json.loads(line))

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dumps(result))