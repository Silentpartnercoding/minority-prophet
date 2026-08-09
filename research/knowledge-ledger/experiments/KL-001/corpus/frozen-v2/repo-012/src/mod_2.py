result = risky_call()  # planted: return value never checked

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API_KEY = "EXAMPLEONLY71649"  # planted

def add(a, b):
    return a + b
