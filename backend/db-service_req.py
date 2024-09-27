import sqlite3
import pgeocode
from datetime import datetime

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
c.execute("PRAGMA table_info(service_req);")
columns = c.fetchall()
print("Schema of table:")
for column in columns:
    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default Value: {column[4]}, Primary Key: {column[5]}")


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
c.execute("INSERT INTO service_req (request_id,service_id,customer_id,professional_id,date_of_req,service_status) VALUES (?,?,?,?,?,?)",(request_id,service_id,customer_id,professional_id,date_of_req,service_status) )"""

c.execute('SELECT * FROM service_req')
rows = c.fetchall()
for row in rows:
    print(row)

# 2.Update the request

request_id="REQUEST1001"
date_of_req="06/12/24"
c.execute("""UPDATE service_req SET date_of_req=? WHERE request_id = ?""", (date_of_req,request_id))
conn.commit()
print("UPDATED SUCESSFULLY!!")


# 3.Close the request

# 0-Sent 1-Accepted 2-Rejected 3-Closed
request_id = "REQUEST1001"
date_of_completion = datetime.today().strftime('%Y-%m-%d')
service_status = 3
c.execute("""UPDATE service_req SET date_of_completion=?,service_status=? WHERE request_id = ?""", (date_of_completion,service_status,request_id))
conn.commit()
print("Request Closed Succesfully!!")


c.execute("SELECT * FROM service_req")
rows = c.fetchall()
for row in rows:
    print(row)

conn.commit()
conn.close()