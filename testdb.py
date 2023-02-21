import sqlite3

conn = sqlite3.connect('test.db')

print ("Opened database successfully");

conn.execute('''CREATE TABLE IF NOT EXISTS “users” (
                “username” TEXT,
                “password” TEXT);''')
print ("Table created successfully");

conn.close()
