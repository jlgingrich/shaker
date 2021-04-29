```
               .                       .           __.....__              
             .'|                     .'|       .-''         '.            
            <  |                   .'  |      /     .-''"'-.  `. .-,.--.  
             | |             __   <    |     /     /________\   \|  .-. | 
         _   | | .'''-.   .:--.'.  |   | ____|                  || |  | | 
       .' |  | |/.'''. \ / |   \ | |   | \ .'\    .-------------'| |  | | 
      .   | /|  /    | | `" __ | | |   |/  .  \    '-.____...---.| |  '-  
    .'.'| |//| |     | |  .'.''| | |    /\  \  `.             .' | |      
  .'.'.-'  / | |     | | / /   | |_|   |  \  \   `''-...... -'   | |      
  .'   \_.'  | '.    | '.\ \._,\ '/'    \  \  \                  |_|      
             '---'   '---'`--'  `"'------'  '---'                         
```

## Overview

**Shaker** is a command-line password management system built using MySQL and Python. It safely stores multiple users' passwords as an encrypted binary token inside a MySQL database through Fernet symmetric encryption. The Fernet encryption function is initialized by the *salt* and *pepper* the user enters into the system at the start of a session, both of which can be arbitrarily long and complex to allow for increased security. Once initialized with these parameters, the system allows the user to store and query, as well as assign a simple identifier to the current state of the encryption function that will be retrieved when the function is initialized with the same *salt* and *pepper*, essentially a username.

## Installation

**Shaker** requires a connection to a running MySQL server to function. This connection is passed to the script as a MySQL connection object, defined in [`shakercon.py`](https://github.com/jlgingrich/shaker/blob/21ad8fabfe27eb930e282ec27ca70398afeb3ee4/shakercon.py), an example of which is provided in this repository. The syntax is as follows:

```
"shakercon.py"

from mysql.connector import connection

con = connection.MySQLConnection(
    host = "<MySQL host>",
    user = "<user>",
    password = "<server password>"
)
```

The user assigned to **Shaker** should be given read and write access, and if automatic setup is desired, be allowed to modify database schemas. Upon sucessfully connecting to a server for the first time, **Shaker** will automatically create the database schema and relations needed for operation.

## Commands

This information can also be requested while running the system with the `help` command.

```
pass set <title> <key> *<"note">: Securely stores <key> under <title>, attaching an optional <note> in parentheses
pass get <title>: Retrieves the key and note, if any, stored under <title>
pass del <title>: Verifies and removes the key under <title>
pass list: Lists all titles with keys
user set <name>: Securely assigns the username <name> to the current session
user get <name>: Gets the username assigned to the current session, if any
help: Gets a list of Shaker commands
exit: Terminates Shaker
```
