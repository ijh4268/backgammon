import sys
import json
from sort_backend import sort

# The block comment below is from a tutorial on taking input from stdin
'''stdin_fileno = sys.stdin
 
# Keeps reading from stdin and quits only if the word 'exit' is there
# This loop, by default does not terminate, since stdin is open
for line in stdin_fileno:
    # Remove trailing newline characters using strip()
    if 'exit' == line.strip():
        print('Found exit. Terminating the program')
        exit(0)
    else:
        print('Message from sys.stdin: {}'.format(line))''' 
# End of block comment

data = []
n = 10 

"""
Function to validate incoming JSON data
"""
def validate(data):
    try:
        json.loads(data)
    except json.JSONDecodeError:
        return False
    return True

# Add JSON data to a list of all data
if validate(sys.stdin): data.append(json.loads(sys.stdin))

# Filter out any unwanted data
filtered = filter(lambda x: "content" in x, data)

for item in filtered:
    if type(item.value) is not int:
        del(item)

chunks = [filtered[i * n:(i+1) * n] for i in range(len(filtered) + n - 1)]

sorted = []
for chunk in chunks:
    sorted.append(sort(chunk))

sorted_json = json.dump(sorted)

sys.stdout.flush()
sys.stdout.write(sorted_json)



