import sqlite3 as sq
con=sq.connect("attendance.db")
cur=con.cursor()
# cur.execute("CREATE TABLE admin(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE,password TEXT)")
# cur.execute("INSERT INTO admin (email, password)VALUES ('admin@gmail.com', 'admin123');")
# cur.execute("drop table students")
# cur.execute("CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT,roll_no TEXT UNIQUE,name TEXT,department TEXT);")
# cur.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id INTEGER,date TEXT,status TEXT,FOREIGN KEY(student_id) REFERENCES students(id));")
# cur.execute("CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT UNIQUE,password TEXT);")
cur.execute("CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT,roll_no TEXT UNIQUE,name TEXT,department TEXT,teacher_id INTEGER,FOREIGN KEY (teacher_id) REFERENCES teachers(id));")

con.commit()
con.close()