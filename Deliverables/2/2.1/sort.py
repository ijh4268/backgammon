import sys

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

def myCont(x):
    return x['content']

array = []

for obj in sys.stdin:
    if 'exit' == obj.strip():
        print('Found exit. Terminating the program')
        break
    else:
        array.append(obj)

print(array.sort(key=myCont))