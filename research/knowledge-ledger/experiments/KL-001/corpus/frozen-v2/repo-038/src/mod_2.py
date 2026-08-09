result = risky_call()  # planted: return value never checked

try:
    step()
except:  # planted: bare except
    pass

def add(a, b):
    return a + b

def add(a, b):
    return a + b

def add(a, b):
    return a + b
