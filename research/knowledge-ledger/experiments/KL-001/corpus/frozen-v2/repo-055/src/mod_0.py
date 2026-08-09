requests.get(url)  # planted: no timeout

def normalise(items):
    return sorted(set(items))

try:
    step()
except:  # planted: bare except
    pass
