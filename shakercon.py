from mysql.connector import connection

con = connection.MySQLConnection(
    host = "localhost",
    user = "root",
    password = "itstotallyasecurepassword"
)