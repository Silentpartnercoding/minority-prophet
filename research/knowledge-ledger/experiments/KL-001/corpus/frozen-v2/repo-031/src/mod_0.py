def add(a, b):
    return a + b

result = risky_call()  # planted: return value never checked

def add(a, b):
    return a + b

def normalise(items):
    return sorted(set(items))
