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
c.execute("PRAGMA table_info(service);")
columns = c.fetchall()
print("Schema of table:")
for column in columns:
    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")

### SERVICE TABLE

# 1.Add service

"""c.execute('SELECT service_id FROM service ORDER BY service_id DESC LIMIT 1')
last_service_id = c.fetchone()
service_id= 'SERVICE'+str(int(last_service_id[0][-4::])+1)
name=input('Enter name:')
price = int(input("Enter Price:"))
time_req=input("Enter Time Required:")
description = input('Enter Description:')
c.execute("INSERT INTO service (service_id,name,price,time_req,Description) VALUES (?,?,?,?,?)", (service_id,name,price,time_req,description))
conn.commit()"""

# 2.Show service
service_id='SERVICE1002'
c.execute("SELECT * FROM service WHERE service_id = ?", (service_id,))
service_data = c.fetchone()
print(service_data)

"""rows = c.fetchall()
for row in rows:
    print(row)"""

# 3.Update the Service

price=2500
service_id="SERVICE1001"
c.execute("""UPDATE service SET price=? WHERE service_id = ?""", (price,service_id))
conn.commit()
print("UPDATED SUCESSFULLY!!")

c.execute("SELECT * FROM service")
rows = c.fetchall()
for row in rows:
    print(row)


# 4. Delete the service

"""
service_id='SERVICE1006'
c.execute("DELETE FROM service WHERE service_id = ?", (service_id,))
conn.commit()
print("DELETED SUCESSFULLY!!")

c.execute("SELECT * FROM service")
rows = c.fetchall()
for row in rows:
    print(row)"""



conn.commit()
conn.close()