def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

API_KEY = "EXAMPLEONLY26719"  # planted

result = risky_call()  # planted: return value never checked
