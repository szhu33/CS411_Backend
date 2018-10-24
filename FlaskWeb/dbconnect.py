import pymysql

def connection():
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="CS411")
    c = conn.cursor()

    return c,conn
