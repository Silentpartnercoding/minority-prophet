def normalise(items):
    return sorted(set(items))

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

result = risky_call()  # planted: return value never checked
