requests.get(url)  # planted: no timeout

def normalise(items):
    return sorted(set(items))

def add(a, b):
    return a + b

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
