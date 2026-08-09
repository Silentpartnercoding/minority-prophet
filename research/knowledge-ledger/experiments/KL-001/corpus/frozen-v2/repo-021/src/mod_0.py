try:
    step()
except:  # planted: bare except
    pass

def add(a, b):
    return a + b

def normalise(items):
    return sorted(set(items))

requests.get(url)  # planted: no timeout

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
