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
c.execute("PRAGMA table_info(customer_review);")
columns = c.fetchall()
print("Schema of table:")
for column in columns:
    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")

### SERVICE TABLE

# 1.Add service

#c.execute('''insert into service values('SERVICE1005','Carpenter',1800,'1.5 Hour','Carpenter is all about making and repairing wooden furniture')''')

# 2.Show service
c.execute('SELECT * FROM user')
rows = c.fetchall()
for row in rows:
    print(row)
"""
# 3.Update Service 


### Customer Table

# 1.Add data
#c.execute('''insert into customer values('ravi_18','CUSTOMER1004','Ravi Makwana','ravi@gmail.com','Jamnagar',361142)''')

c.execute('SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1')
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

# 2.Show all the data
c.execute('SELECT * FROM customer')
rows = c.fetchall()
for row in rows:
    print(row)

#### Professional Table

#1. Add Data

c.execute('SELECT proffesional_id FROM proffesional ORDER BY proffesional_id DESC LIMIT 1')
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
c.execute("INSERT INTO user (username,password,role) VALUES (?,?,?)",(username,password,role))

#2. Show data

c.execute('SELECT * FROM proffesional')
rows = c.fetchall()
for row in rows:
    print(row)
"""
#3. update data



#### Service Request 

# 1.Add Data

"""c.execute('SELECT request_id FROM service_req ORDER BY request_id DESC LIMIT 1')
last_request_id = c.fetchone()
request_id=  'REQUEST'+str(int(last_request_id[0][-4::])+1)
service_id = input("Enter Service ID:")
customer_id = input("Enter CUSTOMER ID:")
professional_id = input("Enter Professional ID:")
date_of_req=input('Date of Request:')
service_status = 0
c.execute("INSERT INTO service_req (request_id,service_id,customer_id,professional_id,date_of_req,service_status) VALUES (?,?,?,?,?,?)",(request_id,service_id,customer_id,professional_id,date_of_req,service_status) )

c.execute('SELECT * FROM service_req')
rows = c.fetchall()
for row in rows:
    print(row)"""



#### Review Table

# 1.Add Data

customer_id = input("Enter CUSTOMER ID:")
professional_id = input("Enter Professional ID:")
review=input('Enter Review:')
stars=int(input('Enter Rating:'))
c.execute("INSERT INTO customer_review (customer_id,proffesional_id,review,stars) VALUES (?,?,?,?)",(customer_id,professional_id,review,stars) )

c.execute('SELECT * FROM customer_review')
rows = c.fetchall()
for row in rows:
    print(row)



conn.commit()
conn.close()