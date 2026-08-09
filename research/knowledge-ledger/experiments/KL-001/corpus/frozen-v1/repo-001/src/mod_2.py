requests.get(url)  # planted: no timeout

def normalise(items):
    return sorted(set(items))
