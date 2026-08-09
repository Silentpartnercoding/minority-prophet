def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

requests.get(url)  # planted: no timeout

result = risky_call()  # planted: return value never checked

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
