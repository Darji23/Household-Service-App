from flask_mail import Message
from datetime import datetime, timedelta
import pytz
from app import mail, celery, app
import sqlite3

conn=sqlite3.connect('site.db')
c=conn.cursor()
print("Connection Succesful")

# Set the timezone to IST (Asia/Kolkata)
timezone = pytz.timezone('Asia/Kolkata')

# Celery task to send emails asynchronously to multiple recipients
@celery.task
def send_async_email(recipients, subject, body):
    with app.app_context():  # Flask context to use Flask's mail instance
        for to_email in recipients:
            msg = Message(subject, recipients=[to_email])
            msg.body = body
            mail.send(msg)


# Celery task to send the scheduled email at 7:30 PM IST
@celery.task
def send_scheduled_email():
    with app.app_context():
        c.execute("SELECT * FROM proffesional WHERE proffesional.proffesional_id IN (SELECT service_req.professional_id FROM service_req WHERE service_status = 1);")
        rows = c.fetchall()
        receipients=[]
        names=[]
        for row in rows:
            receipients.append([row[3]])
            names.append(row[2])
        
        for i in range(len(receipients)):
            subject = "Pending Works for Today!!"
            body = f"Hello {names[i]}, There is some pending work for today!!"
            receipient = receipients[i]
            send_async_email(receipient, subject, body)
        
        
        

# Celery task to send the scheduled email at 7:30 PM IST every month
@celery.task
def send_monthly_email():
    with app.app_context():
        recipients = [
            'abhishekdarji653@gmail.com',
            '21DCS014@CHARUSAT.EDU.IN',
            'darjiabhishek739@gmail.com'
        ]
        subject = "Scheduled Email"
        body = "This email was sent automatically for monthly reminder"
        
        send_async_email(recipients, subject, body)


# Function to get the next run time for a specific hour and minute
def get_next_run_time(hour, minute):
    now = datetime.now(timezone)
    scheduled_time = timezone.localize(datetime(now.year, now.month, now.day, hour, minute))

    # If the current time is past the scheduled time, schedule for the next day
    if now > scheduled_time:
        scheduled_time += timedelta(days=1)

    return scheduled_time

def get_next_monthly_run_time(hour, minute):
    now = datetime.now(timezone)
    
    # Determine the scheduled time for the 1st of the next month
    year = now.year
    month = now.month + 1 if now.month < 12 else 1
    year = year + 1 if month == 1 else year
    
    scheduled_time = timezone.localize(datetime(year, month, 27, hour, minute))
    
    # If the current date is before the 1st, schedule for this month
    if now.day == 27 and now.time() < scheduled_time.time():
        scheduled_time = timezone.localize(datetime(now.year, now.month, 27, hour, minute))
    
    return scheduled_time

# Function to schedule tasks based on their name
def schedule_task(task_name):

    if task_name == 'send_scheduled_email':
        eta = get_next_run_time(0, 11)  # Schedule for 7:30 PM IST
        send_scheduled_email.apply_async(eta=eta)
        print(f"Email task scheduled for: {eta}")
        
    elif task_name == 'send_monthly_email':
        eta = get_next_monthly_run_time(20, 7)  # Schedule for 6:30 PM IST on the 1st
        send_monthly_email.apply_async(eta=eta)
        print(f"Monthly email task scheduled for: {eta}")
