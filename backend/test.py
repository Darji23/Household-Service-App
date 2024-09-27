import sqlite3


conn=sqlite3.connect('backend/site.db')
c=conn.cursor()
print("Connection Succesful")

c.execute("SELECT * FROM proffesional WHERE proffesional.proffesional_id IN (SELECT service_req.professional_id FROM service_req WHERE service_status = 1);")
rows = c.fetchall()
receipients=[]
names=[]
for row in rows:
    receipients.append([row[3]])
    names.append(row[2])

print(receipients)
print(names)