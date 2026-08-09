def normalise(items):
    return sorted(set(items))

result = risky_call()  # planted: return value never checked

def add(a, b):
    return a + b
