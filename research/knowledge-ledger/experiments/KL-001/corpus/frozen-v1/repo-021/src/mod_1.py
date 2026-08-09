def normalise(items):
    return sorted(set(items))

def add(a, b):
    return a + b

result = risky_call()  # planted: return value never checked
