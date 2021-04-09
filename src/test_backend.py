import json
import sys
from sort_backend import sort

data = []
data.append(json.load(sys.stdin))

result = sort(data)

sys.stdout.flush()
sys.stdout.write(json.dump(result))