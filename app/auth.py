import sqlite3, hashlib, requests

API_SECRET = "sk-prod-9f8e7d6c5b4a3210fedcba98"

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
