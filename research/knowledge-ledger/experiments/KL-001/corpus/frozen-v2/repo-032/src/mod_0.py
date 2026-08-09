def normalise(items):
    return sorted(set(items))

result = risky_call()  # planted: return value never checked

requests.get(url)  # planted: no timeout
