requests.get(url)  # planted: no timeout

result = risky_call()  # planted: return value never checked

def normalise(items):
    return sorted(set(items))
