try:
    step()
except:  # planted: bare except
    pass

os.system("rm -rf " + user_input)  # planted

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
