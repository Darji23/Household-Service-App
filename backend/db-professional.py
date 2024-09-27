import sqlite3
import pgeocode


conn=sqlite3.connect('backend\site.db')
c=conn.cursor()
nomi = pgeocode.Nominatim('IN')
print("Connection Succesful")

# 1.Query to get the names of the tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# 2.Execute PRAGMA to get the table structure
c.execute("PRAGMA table_info(proffesional);")
columns = c.fetchall()
print("Schema of table:")
for column in columns:
    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")

#### Professional Table

#1. Add Data

"""c.execute('SELECT proffesional_id FROM proffesional ORDER BY proffesional_id DESC LIMIT 1')
last_professional_id = c.fetchone()
username = input('Enter Username:')
professional_id= 'PROFESSIONAL'+str(int(last_professional_id[0][-4::])+1)
name=input('Enter name:')
description = input('Enter Description:')
email_id=input("Enter Email ID:")
pincode = int(input("Enter Pincode:"))
service_id = input("Enter Service ID:")
verification = 1
password = input("Enter Password:")
role="PROFESSIONAL"
c.execute("INSERT INTO proffesional (proffesional_id,username,name,email_id,description,service_id,pincode,verification) VALUES (?,?,?,?,?,?,?,?)", (professional_id,username,name,email_id,description,service_id,pincode,verification))
c.execute("INSERT INTO user (username,password,role) VALUES (?,?,?)",(username,password,role))"""

#2. Show data

c.execute('SELECT * FROM proffesional')
rows = c.fetchall()
for row in rows:
    print(row)


# 3.Update the verification status -- Admin

# 1-Pending 2-Accepted 0-Rejected 3-Blocked

verification=2
proffesional_id="PROFESSIONAL1001"
c.execute("""UPDATE proffesional SET verification=? WHERE proffesional_id = ?""", (verification,proffesional_id))
conn.commit()
print("CHANGE COMMITED SUCCESFULLY!!!!")

c.execute('SELECT * FROM proffesional')
rows = c.fetchall()
for row in rows:
    print(row)


# 5. Search Services according to location

print("Found the professional!!! ")
pincode=361142
c.execute("SELECT * FROM proffesional WHERE pincode=?", (pincode,))
rows = c.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()