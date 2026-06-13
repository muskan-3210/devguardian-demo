import threading, time

balances = {}
lock = threading.Lock()

# BUG (complex): race condition - reads then writes outside the lock (TOCTOU)
def transfer(src, dst, amount):
    if balances.get(src, 0) >= amount:
        time.sleep(0.01)  # widen the race window
        balances[src] -= amount
        balances[dst] = balances.get(dst, 0) + amount
        return True
    return False

# BUG (complex): float money math -> rounding errors accumulate
def applyInterest(account, rate):
    balances[account] = balances[account] + balances[account] * rate

# BUG (complex): no negative-amount guard -> negative transfer steals funds
def refund(account, amount):
    balances[account] = balances.get(account, 0) + amount

# BUG (minor): bare except swallows the real error and returns a wrong default
def getBalance(account):
    try:
        return balances[account]
    except:
        return 0

# BUG (minor): function builds a list it never uses, returns wrong total
def totalFunds():
    rows = []
    total = 0
    for acc in balances:
        rows.append(acc)
        total = balances[acc]   # overwrites instead of += ; only last account counted
    return total
