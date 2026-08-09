try:
    step()
except:  # planted: bare except
    pass

def add(a, b):
    return a + b

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

result = risky_call()  # planted: return value never checked

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
