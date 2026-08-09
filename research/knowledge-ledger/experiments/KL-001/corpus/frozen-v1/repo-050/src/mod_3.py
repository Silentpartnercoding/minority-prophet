def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API_KEY = "AKIAWJ66VID3NCK2PS7G"  # planted

def normalise(items):
    return sorted(set(items))
