import sqlite3

conn = sqlite3.connect("sophia.db")

cursor = conn.cursor()
query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)


# To insert values

# query = "INSERT INTO sys_command VALUES (null, 'OBS Studio', 'C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe')"
# cursor.execute(query)
# conn.commit()
# conn.close()


query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# To insert values

query = "INSERT INTO web_command VALUES (null, 'GitHub', 'https://github.com')"
cursor.execute(query)
conn.commit()
conn.close()