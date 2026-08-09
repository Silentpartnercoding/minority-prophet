def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

def normalise(items):
    return sorted(set(items))

try:
    step()
except:  # planted: bare except
    pass

def add(a, b):
    return a + b
