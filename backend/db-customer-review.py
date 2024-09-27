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