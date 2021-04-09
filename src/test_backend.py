import json
import sys
from sort_backend import sort

data = []

for line in sys.stdin:
  data.append(line)

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dump(result))