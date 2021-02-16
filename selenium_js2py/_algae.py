import re

def enclosedby(string, pattern):
    return string.startswith(pattern) and string.endswith(pattern)

def noneoremptystr(string): return string.strip() if string and string.strip() else ""

def findargs(string): return re.findall(r"arguments\[\d+]", string)

def jio_repr(type_, value):
    return f"@{type_.__name__ if isinstance(type_, type) else type_}:{{{value}}}"

def setupargs(indexer, start, stop):
    return [f"arguments[{indexer(i)}]" for i in range(start, stop)]