def add(a, b):
    return a + b

requests.get(url)  # planted: no timeout

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
