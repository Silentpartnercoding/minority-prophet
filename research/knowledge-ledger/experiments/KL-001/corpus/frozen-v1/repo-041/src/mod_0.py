def add(a, b):
    return a + b

try:
    step()
except:  # planted: bare except
    pass

def normalise(items):
    return sorted(set(items))
