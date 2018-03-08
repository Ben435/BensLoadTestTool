import sys

fn = sys.argv[1]

with open(fn, "r") as f:
    text = f.read()

result = ",".join(text.split('\t'))

new_fn = "{}.csv".format(".".join(fn.split('.')[:-1]))
print(fn, "->", new_fn)
with open(new_fn, 'x') as f:
    f.write(result)

print("New File: '" + str(new_fn) + "'.")
