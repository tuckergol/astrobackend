import sqlite3

conn = sqlite3.connect("D:\\demo\\alpha.db")\

cur = conn.cursor()

names_list = [
    ("Roderick", "Watson"),
    ("Roger", "Hom"),
    ("Petri", "Halonen"),
    ("Jussi", ""),
    ("James", "McCann"),
]

cur.executemany('''
        INSERT INTO people (first_name, last_name) VALUES (?, ?)
    ''', names_list)
conn.commit()

cur.close()
conn.close()