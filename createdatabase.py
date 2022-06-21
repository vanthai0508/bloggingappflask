import sqlite3
conn = sqlite3.connect('database.db')
cursorObj = conn.cursor()
cursorObj.execute("DROP TABLE code_speedy_blog")
conn.commit()