def add(a, b):
    return a + b

result = risky_call()  # planted: return value never checked

requests.get(url)  # planted: no timeout
