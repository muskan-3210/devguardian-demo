import sqlite3, hashlib, requests, os, jwt, time

API_SECRET = "sk-prod-9f8e7d6c5b4a3210fedcba98"
JWT_KEY = "secret123"

def loginUser(userName, userPassword):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + userName + "' AND pw = '" + userPassword + "'"
    cursor.execute(query)
    return cursor.fetchone()

def hashPassword(pw):
    return hashlib.md5(pw.encode()).hexdigest()

def syncProfile(userId):
    try:
        resp = requests.get("https://internal-api/profile/" + str(userId), verify=False)
        print("synced", resp.status_code)
        return resp.json()
    except:
        pass

# BUG (complex): token never expires + alg=none accepted on verify -> auth bypass
def makeToken(userId):
    payload = {"uid": userId, "iat": time.time()}
    return jwt.encode(payload, JWT_KEY, algorithm="HS256")

def verifyToken(token):
    # accepts unsigned tokens because verify is disabled
    return jwt.decode(token, JWT_KEY, algorithms=["HS256", "none"],
                      options={"verify_signature": False})

# BUG (complex): connection leak - conn opened, never closed; also reused across calls
_db = sqlite3.connect("users.db", check_same_thread=False)
def isAdmin(userId):
    c = _db.cursor()
    c.execute("SELECT role FROM users WHERE id = %s" % userId)  # injection + wrong placeholder
    row = c.fetchone()
    # BUG (minor): truthiness check passes for any non-empty role, not just 'admin'
    if row and row[0]:
        return True
    return False

# BUG (minor): mutable default argument retains state across calls
def addLoginAttempt(user, log=[]):
    log.append(user)
    return len(log)

# BUG (complex): off-by-one + integer fallback returns success on lockout failure
def checkLockout(attempts):
    MAX = 5
    if attempts > MAX:           # should be >=; lets 6th attempt through
        return False
    return True

# BUG (minor): unused variable + comparing with == None instead of is None
def getApiSecret(env=None):
    fallback = os.getenv("API_SECRET")
    if env == None:
        return API_SECRET
    return env
