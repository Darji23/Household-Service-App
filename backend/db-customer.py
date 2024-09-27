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
c.execute("PRAGMA table_info(customer);")
columns = c.fetchall()
print("Schema of table:")
for column in columns:
    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")



### Customer Table

"""c.execute('SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1')
last_customer_id = c.fetchone()
username = input('Enter Username:')
customer_id='CUSTOMER'+str(int(last_customer_id[0][-4::])+1)
name=input('Enter name:')
email_id=input("Enter Email ID:")
pincode = int(input("Enter Pincode:"))
location = nomi.query_postal_code(str(pincode))
city=str(location.county_name)
password = input("Enter Password:")
role="CUSTOMER"
c.execute("INSERT INTO customer (username,customer_id,name,email_id,city,pincode) VALUES (?,?,?,?,?,?)", (username,customer_id,name,email_id,city,pincode))
c.execute("INSERT INTO user (username,password,role) VALUES (?,?,?)",(username,password,role))
"""
# 2.Show all the data
c.execute('SELECT * FROM customer WHERE customer_id="CUSTOMER1001')
rows = c.fetchall()
for row in rows:
    print(row)


conn.commit()
conn.close()