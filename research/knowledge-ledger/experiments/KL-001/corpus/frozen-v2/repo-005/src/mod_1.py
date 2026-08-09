def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

try:
    step()
except:  # planted: bare except
    pass
