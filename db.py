import mysql.connector

def getConnection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="tiru",
        database="mybank"
    )
    return conn