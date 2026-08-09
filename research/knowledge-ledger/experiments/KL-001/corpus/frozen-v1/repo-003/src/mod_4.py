def add(a, b):
    return a + b

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

def normalise(items):
    return sorted(set(items))

result = risky_call()  # planted: return value never checked
