from flask import Flask, jsonify
from flask_mail import Mail, Message
from celery import Celery
from datetime import timedelta
import os

# ==========================
# 1. Flask Application Setup
# ==========================

app = Flask(__name__)

# ==========================
# 2. Flask-Mail Configuration
# ==========================

# Configure Flask-Mail with your email server settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'       # e.g., Gmail SMTP server
app.config['MAIL_PORT'] = 465                      # SSL port for Gmail
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Fetch from environment variable
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Fetch from environment variable
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Sender email

mail = Mail(app)

# ==========================
# 3. Celery Configuration
# ==========================

def make_celery(app):
    # Initialize Celery with the Flask app's config
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',   # Redis backend
        broker='redis://localhost:6379/0'     # Redis broker
    )
    celery.conf.update(app.config)
    
    # Define a subclass of Task that wraps the task execution in the Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# ==========================
# 4. Define the Email Sending Function
# ==========================

def send_email(to, subject, body):
    """
    Sends an email using Flask-Mail.
    """
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

# ==========================
# 5. Define the Celery Task
# ==========================

@celery.task(name='app.send_daily_reminders')
def send_daily_reminders():
    """
    Celery task to send reminders to service professionals every 5 minutes.
    """
    professionals = get_professionals_with_pending_requests()
    
    for pro in professionals:
        subject = "Reminder: Pending Service Requests"
        body = f"Hello {pro['name']},\n\nYou have pending service requests. Please visit the platform to accept/reject them."
        send_email(pro['email'], subject, body)
    
    return f"Sent reminders to {len(professionals)} professionals."

# ==========================
# 6. Helper Function to Fetch Professionals
# ==========================

def get_professionals_with_pending_requests():
    """
    Fetches professionals with pending service requests.
    Replace this with actual database queries.
    """
    # Placeholder data. Replace with real database queries.
    return [
        {"email": "pro1@example.com", "name": "Professional 1"},
        {"email": "pro2@example.com", "name": "Professional 2"},
        # Add more professionals as needed
    ]

# ==========================
# 7. Configure Celery Beat Schedule to Send Every 5 Minutes
# ==========================

celery.conf.beat_schedule = {
    'send-email-every-5-minutes': {
        'task': 'app.send_daily_reminders',
        'schedule': timedelta(minutes=5),  # Set the interval to 5 minutes
    },
}

celery.conf.timezone = 'UTC'  # Set to your timezone if needed

# ==========================
# 8. Define a Test Route (Optional)
# ==========================

@app.route('/')
def index():
    return jsonify({"message": "Flask-Celery-Redis Mail Integration with 5-min schedule is Running."})

# ==========================
# 9. Run the Flask Application
# ==========================

if __name__ == '__main__':
    app.run(debug=True)
