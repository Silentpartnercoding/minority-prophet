def normalise(items):
    return sorted(set(items))

try:
    step()
except:  # planted: bare except
    pass

result = risky_call()  # planted: return value never checked
