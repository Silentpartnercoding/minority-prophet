def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

def normalise(items):
    return sorted(set(items))

def add(a, b):
    return a + b

API_KEY = "EXAMPLEONLY70752"  # planted

result = risky_call()  # planted: return value never checked
