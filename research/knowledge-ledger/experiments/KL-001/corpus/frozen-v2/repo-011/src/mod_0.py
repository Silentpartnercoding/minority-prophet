def add(a, b):
    return a + b

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

os.system("rm -rf " + user_input)  # planted

result = risky_call()  # planted: return value never checked
