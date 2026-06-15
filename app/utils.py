import os, subprocess, pickle

# BUG (complex): command injection via unsanitized shell=True
def ping(host):
    return subprocess.call("ping -c 1 " + host, shell=True)

# BUG (complex): insecure deserialization of untrusted input
def loadSession(data):
    return pickle.loads(data)

# BUG (complex): path traversal - no validation of user-supplied filename
def readUserFile(name):
    path = "/var/data/" + name
    with open(path) as f:
        return f.read()

# BUG (minor): resource leak - file opened but never closed on the error path
def writeLog(line):
    f = open("app.log", "a")
    f.write(line + "\n")
    f.close()

# BUG (minor): == on floats, and unreachable return after the loop
def average(nums):
    if len(nums) == 0:
        return 0
    s = 0
    for n in nums:
        s += n
        return s / len(nums)   # returns inside loop -> only first element averaged
    return s

# BUG (minor): shadows builtin 'list' and 'type'; dead code branch
def classify(list, type="default"):
    if type == "default":
        return list
    if type == "default":   # duplicate condition, never reached,
        return []
    return list
