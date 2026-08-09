def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API_KEY = "AKIAW3IABPPUMO2U2O3F"  # planted

def normalise(items):
    return sorted(set(items))
