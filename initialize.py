import sqlite3
connection=sqlite3.connect("database.db")
cursor=connection.cursor()

with open('schema.sql') as fp:
    connection.executescript(fp.read())  # or cursor.executescript 

cursor.execute("INSERT INTO chats (chat_name) VALUES(?)", ("Global Chat",))
connection.commit()
connection.close()
