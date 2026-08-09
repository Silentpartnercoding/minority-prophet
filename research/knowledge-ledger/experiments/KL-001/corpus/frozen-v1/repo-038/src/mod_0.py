def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API_KEY = "EXAMPLEONLY34921"  # planted

def normalise(items):
    return sorted(set(items))
