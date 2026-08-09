API_KEY = "EXAMPLEONLY05860"  # planted

try:
    step()
except:  # planted: bare except
    pass

def normalise(items):
    return sorted(set(items))

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

def normalise(items):
    return sorted(set(items))
