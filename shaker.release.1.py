import mysql.connector
from mysql.connector import errorcode
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import sys

#               .                       .           __.....__              
#             .'|                     .'|       .-''         '.            
#            <  |                   .'  |      /     .-''"'-.  `. .-,.--.  
#             | |             __   <    |     /     /________\   \|  .-. | 
#         _   | | .'''-.   .:--.'.  |   | ____|                  || |  | | 
#       .' |  | |/.'''. \ / |   \ | |   | \ .'\    .-------------'| |  | | 
#      .   | /|  /    | | `" __ | | |   |/  .  \    '-.____...---.| |  '-  
#    .'.'| |//| |     | |  .'.''| | |    /\  \  `.             .' | |      
#  .'.'.-'  / | |     | | / /   | |_|   |  \  \   `''-...... -'   | |      
#  .'   \_.'  | '.    | '.\ \._,\ '/'    \  \  \                  |_|      
#             '---'   '---'`--'  `"'------'  '---'                         

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format("shakercore"))
    except mysql.connector.Error as err:
        print("Failed to create database: {}".format(err))
        exit(1)

def print_header(text="", width=64, pad_char="="):
    if not len(text):
        print(pad_char * width)
        return
    pad = pad_char * ((width - len(text) - 2)//2)
    ret = pad + " " + text + " " + pad
    if len(ret) < width:
        ret += pad_char
    print(ret)

print_header("SHAKER 2.0")

# Get MySQL connection from 'shakercon.py' and attach a cursor
try:
    from shakercon import con
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Incorrect credentials for attempted database connection.")
    else:
        print(err)
    sys.exit()
c = con.cursor()

# Handle connecting to the shakercore database 
try:
    c.execute("USE {}".format("shakercore"))
except mysql.connector.Error as err:
    print("Database {} does not exist.".format("shakercore"))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(c)
        print("Database {} created successfully.".format("shakercore"))
        con.database = "shakercore"
        print_header()
    else:
        print(err)
        sys.exit()


c.execute("""CREATE TABLE IF NOT EXISTS passwords(title CHAR(32) PRIMARY KEY, token BLOB(64) NOT NULL, note CHAR(128));""")
c.execute("""CREATE TABLE IF NOT EXISTS users(token BLOB(64) NOT NULL, name CHAR(32) PRIMARY KEY);""")

# Request session determinants
salt = bytes(input("Salt: "), 'utf-8')
pepper = bytes(input("Pepper: "), 'utf-8')

# Securely generate encryption function
kdf = Scrypt(
    salt=salt,
    length=32,
    n=2**18,
    r=8,
    p=1
)
salt = None
f = Fernet(base64.urlsafe_b64encode(kdf.derive(pepper)))
pepper = None
kdf = None

# If session has a recognized username, welcome the user back
try:
    c.execute("""SELECT * FROM users""")
    ret = c.fetchall()
    if ret == None: raise Exception()
    for token, name in ret:
        try:
            if f.decrypt(token).decode('utf-8') == "username":
                username = name
        except Exception as e:
            continue
    print_header("HELLO, " + username)
except Exception as e:
    print_header("SESSION GO")

# Begin shell
while True:
    con.commit()
    print()
    line = input("> ")
    print()
    args = line.split(" ")
    ret = None
    if args[0].lower() == "pass":
        if args[1].lower() == "set":
            try:
                if len(args) > 3:
                    note = " ".join(args[4:])
                else:
                    note = None
                c.execute("""INSERT INTO passwords VALUES (%s,%s,%s);""", (args[2], f.encrypt(bytes(args[3], 'utf-8')), note))
                print("Stored as '" + args[2] + "'")
            except Exception as e:
                print("Assignment error")
                continue
        elif args[1].lower() == "get":
            try:
                c.execute("""SELECT token, note FROM passwords WHERE title = %s""", (args[2],))
                ret = c.fetchone()
                if ret == None: raise Exception()
            except Exception as e:
                print("Retrieval error")
                continue
            try:
                print(f.decrypt(ret[0]).decode('utf-8'))
                if len(ret[1]):
                    print(ret[1])
            except Exception as e:
                print("Decryption error")
                continue
        elif args[1].lower() == "del":
            try:
                c.execute("""SELECT token FROM passwords WHERE title = %s""", (args[2],))
                ret = c.fetchone()
                if ret == None: raise Exception()
                f.decrypt(ret[0]).decode('utf-8')
            except Exception as e:
                print("Deletion error")
                continue
            try:
                c.execute("""DELETE FROM passwords WHERE title = %s;""", (args[2],))
                print("Removed entry for '" + args[2] + "'")
            except Exception as e:
                print("Deletion error")
                continue
        elif args[1].lower() == "list":
            try:
                c.execute("""SELECT title FROM passwords""")
                ret = c.fetchall()
                if ret == None: raise Exception()
                for name in ret:
                    print(name[0])
            except Exception as e:
                print("Retrieval error")
                continue
        else:
            print("Invalid command")
    elif args[0].lower() == "user":
        if args[1].lower() == "set":
            try:
                exists = False
                c.execute("""SELECT * FROM users""")
                ret = c.fetchall()
                if ret == None: raise Exception()
                for token, name in ret:
                    try:
                        if f.decrypt(token).decode('utf-8') == "username":
                            exists = True
                    except Exception as e:
                        continue
                if exists:
                    print("Username already set")
                    continue
                c.execute("""INSERT INTO users VALUES (%s,%s);""", (f.encrypt(bytes("username", 'utf-8')), args[2]))
                print("Saved")
            except Exception as e:
                print("Assignment error")
                continue
        elif args[1].lower() == "get":
            try:
                c.execute("""SELECT * FROM users""")
                ret = c.fetchall()
                if ret == None: raise Exception()
                for token, name in ret:
                    try:
                        if f.decrypt(token).decode('utf-8') == "username":
                            username = name
                    except Exception as e:
                        continue
                print(username)
            except Exception as e:
                print("Retrieval error")
                continue
        else:
            print("Invalid command")
    elif args[0].lower() == "help":
        print('pass set <title> <key> *<"note">: Securely stores <key> under <title>, attaching an optional <note> in parentheses')
        print("pass get <title>: Retrieves the key and note, if any, stored under <title>")
        print("pass del <title>: Verifies and removes the key under <title>")
        print("pass list: Lists all titles with passwords")
        print("user set <name>: Securely assigns the username <name> to the current session")
        print("user get <name>: Gets the username assigned to the current session, if any")
        print("help: Gets a list of Shaker commands")
        print("exit: Terminates Shaker")
    elif args[0].lower() == "" or args[0].lower() == "exit":
        break
    else:
        print("Invalid command")

# Finalize and close connections
print_header("END SHAKER")
print()
con.commit()
con.close()
