import os
from flask import Flask,render_template,request,redirect,url_for,jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pgeocode
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime
from flask_mail import Mail
from celery import Celery


current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "site.db")
app.config['SECRET_KEY'] = b'\xbe\x8e\xa4\xa0\x83\t\xb3\xe0)3\xe1\x8e\xc9A{J+\x1a\x03]^5(0'
app.config['JWT_SECRET_KEY'] = b'\xbe\x8e\xa4\xa0\x83\t\xb3\xe0)3\xe2\x8e\xc9A{J+\x1a\x02]^5(0'

# Configure Flask-Mail settings
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='abhidarji2004@gmail.com',
    MAIL_PASSWORD='wvkx otln sbco esuc',
    MAIL_DEFAULT_SENDER='abhidarji2004@gmail.com'
)

mail = Mail(app)

# Configure SQLAlchemy
db = SQLAlchemy(app)
jwt = JWTManager(app)
app.app_context().push()
CORS(app) 

# Configure Celery to use Redis
def make_celery(app):
    celery = Celery(app.import_name, broker='redis://localhost:6379/0')
    celery.conf.update(app.config)
    celery.conf.update(result_backend='redis://localhost:6379/0')
    return celery

celery = make_celery(app)


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key=True,unique=True,nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)

    def __init__(self, username, password,role):
        self.username = username
        self.password = password
        self.role = role

    def get_id(self):
        return self.userid

class Customer(db.Model):
    __tablename__ = 'customer'
    username=db.Column(db.String,nullable=False)
    customer_id=db.Column(db.String,primary_key=True,nullable=False)
    name=db.Column(db.String,nullable=False)
    email_id=db.Column(db.String,nullable=False)
    city=db.Column(db.String,nullable=False)
    pincode=db.Column(db.Integer,nullable=False)

class Professional(db.Model):
    __tablename__ = 'proffesional'
    proffesional_id=db.Column(db.String,primary_key=True,nullable=False)
    username=db.Column(db.String,nullable=False)
    name=db.Column(db.String,nullable=False)
    email_id=db.Column(db.String,nullable=False)
    description=db.Column(db.String,nullable=False)
    service_id=db.Column(db.String,db.ForeignKey('service.service_id'),nullable=False)
    pincode=db.Column(db.String,nullable=False)
    verification=db.Column(db.Integer,nullable=False)

class Service(db.Model):
    __tablename__ = 'service'
    service_id=db.Column(db.String,primary_key=True,nullable=False)
    name=db.Column(db.String,nullable=False)
    price=db.Column(db.Integer,nullable=False)
    time_req=db.Column(db.String,nullable=False)
    Description=db.Column(db.String,nullable=False)

class ServiceReq(db.Model):
    __tablename__ = "service_req"
    request_id = db.Column(db.String, primary_key=True, nullable=False)
    service_id = db.Column(db.String, db.ForeignKey('service.service_id'), nullable=False)
    customer_id = db.Column(db.String, db.ForeignKey('customer.customer_id'), nullable=False)  
    professional_id = db.Column(db.String, db.ForeignKey('proffesional.proffesional_id'), nullable=False)
    date_of_req = db.Column(db.String, nullable=False)
    date_of_completion = db.Column(db.String, nullable=False)
    service_status = db.Column(db.Integer, nullable=False)

class CustomerReview(db.Model):
    __tablename__ = "customer_review"
    review_id = db.Column(db.String,primary_key=True,nullable=False)
    request_id=db.Column(db.String,db.ForeignKey('service_req.request_id'))
    professional_id=db.Column(db.String,db.ForeignKey('proffesional.proffesional_id'),nullable=False)
    customer_id=db.Column(db.String,db.ForeignKey('customer.customer_id'),nullable=False)
    review = db.Column(db.String,nullable=False)
    stars = db.Column(db.Integer,nullable=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).first()

    if user:
        if user.password != password:
            return jsonify({"msg": "Bad username or password"}), 401
        else:
            role=user.role
            access_token = create_access_token(identity={"username": username, "role": role})
            return jsonify(access_token=access_token, role=role,username=username)
    else:
        return jsonify({"msg": "Username Not Found!!"}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"msg": "Logout successful"}), 200


# 1.1 Create Customer
@app.route('/customer', methods=['POST'])
def create_customer():
    nomi = pgeocode.Nominatim('IN')
    data = request.get_json()
    last_customer = db.session.query(Customer.customer_id).order_by(Customer.customer_id.desc()).first()
    customer_id = 'CUSTOMER' + str(int(last_customer[0][-4:]) + 1) if last_customer else 'CUSTOMER1001'
    username = data['username']
    name = data['name']
    email_id = data['email_id']
    pincode = data['pincode']
    location = nomi.query_postal_code(str(pincode))
    city = str(location.county_name)
    password = data['password']
    role = "CUSTOMER"
    new_customer = Customer(username=username, customer_id=customer_id, name=name, email_id=email_id, city=city, pincode=pincode)
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_customer)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "Item added successfully!"}, 200

# 1.2 Create Professional
# 1-Pending 2-Accepted 0-Rejected 3-Blocked
@app.route('/professional', methods=['POST'])
def create_professional():
    data = request.get_json()
    last_professional = db.session.query(Professional.proffesional_id).order_by(Professional.proffesional_id.desc()).first()
    proffesional_id = 'PROFESSIONAL' + str(int(last_professional[0][-4:]) + 1) if last_professional else 'PROFESSIONAL1001'
    username = data['username']
    name = data['name']
    email_id = data['email_id']
    pincode = data['pincode']
    description = data['description']
    service_id = data['service_id']
    verification=1
    password = data['password']
    role = "PROFESSIONAL"
    new_professional = Professional(proffesional_id=proffesional_id,username=username,name=name,email_id=email_id,pincode=pincode,description=description,service_id=service_id,verification=verification)
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_professional)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "Item added successfully!"}, 200



# 2.1 Admin Dashboard

# Professionals
@app.route('/AdminData',methods=['GET'])
def adminData():
    customer_data=Customer.query.all()
    professional_data = Professional.query.all()

    customer_list=[]
    for customer in customer_data:
        customer_list.append({
            "username": customer.username,
            "customer_id" : customer.customer_id,
            "name" : customer.name,
            "email_id" : customer.email_id,
            "city" : customer.city,
            "pincode" : customer.pincode
        })
    
    professional_list=[]
    for professional in professional_data:
        professional_list.append({
            "proffesional_id" : professional.proffesional_id,
            "username" : professional.username,
            "name" : professional.name,
            "email_id" : professional.email_id,
            "description": professional.description,
            "service_id": professional.service_id,
            "pincode": professional.pincode,
            "verification": professional.verification
        })
    
    return jsonify({
        "Customer Data":customer_list,
        "Professional Data":professional_list
        })


@app.route('/getProffesionalData',methods=['GET'])
def professional_data():
    professional_data = Professional.query.filter_by(verification=2).all()   
    professional_list=[]
    for professional in professional_data:
        service_id = professional.service_id
        service = Service.query.filter_by(service_id=professional.service_id).first()
        if not service:
            return jsonify({"msg": "Service not found"}), 404
        service_name = service.name
        professional_list.append({
            "proffesional_id" : professional.proffesional_id,
            "username" : professional.username,
            "name" : professional.name,
            "email_id" : professional.email_id,
            "description": professional.description,
            "service_name": service_name,
            "pincode": professional.pincode,
            "verification": professional.verification
        })
    
    return jsonify({
        "Professional Data":professional_list
        })

@app.route('/ProfessionalPending',methods=['GET'])
def professional_pending_data():
    professional_data = Professional.query.filter_by(verification=1).all()   
    professional_list=[]
    for professional in professional_data:
        service_id = professional.service_id
        service = Service.query.filter_by(service_id=professional.service_id).first()
        if not service:
            return jsonify({"msg": "Service not found"}), 404
        service_name = service.name
        professional_list.append({
            "proffesional_id" : professional.proffesional_id,
            "username" : professional.username,
            "name" : professional.name,
            "email_id" : professional.email_id,
            "description": professional.description,
            "service_name": service_name,
            "pincode": professional.pincode,
            "verification": professional.verification
        })
    
    return jsonify({
        "Professional Data":professional_list
        })


@app.route('/getCustomer/<string:username>', methods=['GET'])
def get_customer(username):
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"msg": "Customer not found"}), 404
    # Return customer data as a single object, not a list
    customer_data = {
        "username": customer.username,
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email_id": customer.email_id,
        "city": customer.city,
        "pincode": customer.pincode
    }
    return jsonify(customer_data)

@app.route('/getProfessional/<string:username>', methods=['GET'])
def get_professional(username):
    professional = Professional.query.filter_by(username=username).first()
    if not professional:
        return jsonify({"msg": "Professional not found"}), 404
    service = Service.query.filter_by(service_id=professional.service_id).first()
    if not service:
        return jsonify({"msg": "Service not found"}), 404
    service_name = service.name
    professional_data = {
        "proffesional_id" : professional.proffesional_id,
        "username" : professional.username,
        "name" : professional.name,
        "email_id" : professional.email_id,
        "description": professional.description,
        "service_name": service_name,
        "pincode": professional.pincode,
        "verification": professional.verification
    }
    return jsonify(professional_data)


@app.route('/Admin', methods=['GET'])
def get_admin():
    admin_data = {
        "name": "Administrator",
    }
    return jsonify(admin_data)

# 2.2 Admin Dashboard - Approve/Rejection/Block Professional 
# 0-Rejected 1-Pending 2-Accepted 3-Blocked

@app.route('/Admin/<string:professional_id>/<int:verification_code>', methods=['PUT'])
def acceptProfessional(professional_id, verification_code):
    professional = Professional.query.filter_by(proffesional_id=professional_id).first()
    if professional:
        professional.verification = verification_code
        db.session.commit()
        return {"message": "Updated Successfully!!"}, 200
    else:
        return {"message": "Verification code is not 1 or already updated."}, 400

@app.route('/requests/<string:customer_id>', methods=['GET'])
def get_requests(customer_id):
    request_data = ServiceReq.query.filter_by(customer_id=customer_id).all()
    request_data_list = []
    for request in request_data:
        professional = Professional.query.filter_by(proffesional_id=request.professional_id).first()
        request_data_list.append({
            'request_id': request.request_id,
            'professional_name': professional.name if professional else 'Unknown',
            'request_date': request.date_of_req,  # Ensure this field exists in your DB,
            'completion_date': request.date_of_completion if request.date_of_completion else 'NOT COMPLETED',
            'service_status': request.service_status
        })
    
    return jsonify(request_data_list), 200


# 3.1 Service Managment - Admin - Create Service
@app.route('/service',methods=['POST'])
def createService():
    data = request.get_json()
    last_service = db.session.query(Service.service_id).order_by(Service.service_id.desc()).first()
    service_id = 'SERVICE' + str(int(last_service[0][-4:]) + 1) if last_service else 'SERVICE1001'
    name = data['name']
    price = data['price']
    time_req=data['time_req']
    description=data['description']
    new_service = Service(service_id=service_id,name=name,price=price,time_req=time_req,Description=description)
    db.session.add(new_service)
    db.session.commit()
    return {"message": "Service Created Sucessfully!!"}, 200


@app.route('/service/<string:service_id>', methods=['GET'])
def get_service(service_id):
    service=Service.query.filter_by(service_id=service_id).first()
    if not service:
        return jsonify({"msg": "Service not found"}), 404
    else:
        service_data = {
            "service_id" : service.service_id,
            "name": service.name,
            "price":service.price,
            "time_req":service.time_req,
            "description":service.Description
        }
    professionals_data=Professional.query.filter_by(service_id=service_id).all()
    professional_data_list=[]
    for professional in professionals_data:
         professional_data_list.append({
            "proffesional_id" : professional.proffesional_id,
            "username" : professional.username,
            "name" : professional.name,
            "email_id" : professional.email_id,
            "description": professional.description,
            "service_id": professional.service_id,
            "pincode": professional.pincode,
            "verification": professional.verification
        })
    return jsonify({"service_data":service_data,"professional_data":professional_data_list})


@app.route('/service',methods=['GET'])
def get_service_data():
    service_data=Service.query.all()
    service_list=[]
    for service in service_data:
        service_list.append({
            "service_id" : service.service_id,
            "name": service.name,
            "price":service.price,
            "time_req":service.time_req,
            "description":service.Description
        })
    return jsonify({
        "Professional Data":service_list
    })


@app.route('/getProfessionals/<string:service_id>', methods=['GET'])
def get_professionals_by_service(service_id):
    professionals = Professional.query.filter_by(service_id=service_id,verification=2).all()
    professional_list = [{
        "professional_id": pro.proffesional_id,
        "name": pro.name,
        "pincode": pro.pincode,
        "description": pro.description
    } for pro in professionals]
    return jsonify(professional_list)



# 3.2 Service Management - Admin - Update a service
@app.route('/service/<string:service_id>',methods=['PUT'])
def updateService(service_id):
    data=request.get_json()
    service = Service.query.filter_by(service_id=service_id).first()
    if service:
        service.price=data['price']
        db.session.commit()
        return {"message":"Succesfully Updated"}
    else:
        return {"message":"No Service Found"}


# 3.3. Service Management - Admin - Delete Service
@app.route('/Service/<string:service_id>',methods=['DELETE'])
def deleteService(service_id):
    service = Service.query.filter_by(service_id=service_id).first()
    if service:
        db.session.delete(service)
        db.session.commit()
        return {"message": "Service and related records deleted successfully!"}, 200
    else:
        return {"message": "Service not found!"}, 404


# 4.1 Service Request - Create New Request
@app.route('/ServiceRequest', methods=['POST'])
def create_service_request():
    data = request.get_json()
    last_request = db.session.query(ServiceReq.request_id).order_by(ServiceReq.request_id.desc()).first()
    request_id = 'REQUEST' + str(int(last_request[0][-4:]) + 1) if last_request else 'REQUEST1001'
    service_id=data['service_id']
    customer_id=data['customer_id']
    professional_id=data['professional_id']
    date_of_req=data['date_of_req']
    service_status=0
    new_request=ServiceReq(request_id=request_id,service_id=service_id,customer_id=customer_id,professional_id=professional_id,date_of_req=date_of_req,service_status=service_status)
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Service request created successfully'}), 200


@app.route('/ServiceRequest/<string:professional_id>')
def get_requests_data(professional_id):
    requests_data = ServiceReq.query.filter_by(professional_id=professional_id).all() 
    request_data_list=[]
    for request in requests_data:
        customer=Customer.query.filter_by(customer_id=request.customer_id).first()
        request_data_list.append({
            "request_id":request.request_id,
            "customer_name":customer.name if customer else 'UNKNOWN',
            "request_date":request.date_of_req,
            "date_of_completion":request.date_of_completion,
            'service_status':request.service_status
        })

    sent_requests_data=ServiceReq.query.filter_by(professional_id=professional_id,service_status=0)
    sent_requests_data_list=[]
    for accepted_request in sent_requests_data:
        sent_requests_data_list.append({
            "request_id":accepted_request.request_id,
            "customer_id":accepted_request.customer_id,
            "customer_location":'TBD',
            "date_of_req":accepted_request.date_of_req
        })
    
    pending_requests_data=ServiceReq.query.filter_by(professional_id=professional_id,service_status=1)
    pending_requests_data_list=[]
    for accepted_request in pending_requests_data:
        pending_requests_data_list.append({
            "request_id":accepted_request.request_id,
            "customer_id":accepted_request.customer_id,
            "customer_location":'TBD',
            "date_of_req":accepted_request.date_of_req
        })
    
    return jsonify({
        "Professional Data":request_data_list,
        "Pending Requests":pending_requests_data_list,
        "Sent Requests":sent_requests_data_list
        })


# 4.2 Service Request - Close Request
# 0-Sent 1-Accepted 2-Rejected 3-Closed 4-Cancelled

@app.route('/updateRequest/<string:request_id>', methods=['PUT'])
def update_request(request_id):
    data = request.get_json()
    service = ServiceReq.query.filter_by(request_id=request_id).first()
    
    if service:
        service.service_status = data['service_status']  # Update the service status field
        if data['service_status'] == 3:  # If the status is 'Close', update the date_of_completion
            service.date_of_completion = datetime.utcnow().strftime('%Y-%m-%d')  # Set completion date to today
        db.session.commit()
        return jsonify({
            "message": "Request Successfully Updated",
            "updated_request": {
                "request_id": service.request_id,
                "service_status": service.service_status,
                "date_of_completion": service.date_of_completion
            }
        })
    else:
        return jsonify({"message": "No Request Found"}), 404


@app.route('/NewReview', methods=['POST'])
def new_review():
    data = request.get_json()
    last_review = db.session.query(CustomerReview.review_id).order_by(CustomerReview.review_id.desc()).first()
    review_id = 'REVIEW' + str(int(last_review[0][-4:]) + 1) if last_review else 'REVIEW1001'
    request_id = data.get('request_id')
    professional_id = data.get('professional_id')
    customer_id = data.get('customer_id')
    review = data.get('review')
    stars = data.get('stars')
    new_review = CustomerReview(review_id=review_id,request_id=request_id,professional_id=professional_id,customer_id=customer_id,review=review,stars=stars)
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Review submitted successfully.'})

@app.route('/GetReviews/<string:professional_id>',methods=['GET'])
def get_review(professional_id):
    reviews=CustomerReview.query.filter_by(professional_id=professional_id).all()
    review_list=[]
    for review in reviews:
        customer=Customer.query.filter_by(customer_id=review.customer_id).first()
        request=ServiceReq.query.filter_by(request_id=review.request_id).first()
        review_list.append({
            "request_id":review.request_id,
            "customer_name":customer.name,
            "date_of_completion":request.date_of_completion,
            "review":review.review,
            "stars":review.stars
        })
    return jsonify({
        "review_data":review_list
    })


# 0-Sent 1-Accepted 2-Rejected 3-Closed 4-Cancelled
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    # Correct usage of .count() without calling .all()
    total_professionals = Professional.query.count()
    accepted_professionals = Professional.query.filter_by(verification=2).count()
    blocked_professionals = Professional.query.filter_by(verification=3).count()
    
    professional_data = {
        "total_professionals": total_professionals,
        "accepted_professionals": accepted_professionals,
        "blocked_professionals": blocked_professionals
    }

    # Correct usage of .count() for ServiceReq query
    total_requests = ServiceReq.query.count()
    pending_request = ServiceReq.query.filter_by(service_status=1).count()
    completed_request = ServiceReq.query.filter_by(service_status=3).count()
    rejected_request = ServiceReq.query.filter_by(service_status=2).count()
    cancelled_request = ServiceReq.query.filter_by(service_status=4).count()

    request_data = {
        'total_requests': total_requests,
        'pending_request': pending_request,
        'completed_request': completed_request,
        'rejected_request': rejected_request,
        'cancelled_request': cancelled_request
    }

    # List all services and count professionals per service
    services = Service.query.all()
    professional_count_list = []
    for service in services:
        # Correct usage of .count() for filtering by service_id
        number_of_professionals = Professional.query.filter_by(service_id=service.service_id).count()
        professional_count_list.append({
            'service_id':service.service_id,
            'service_name': service.name,
            'count': number_of_professionals
        })

    return jsonify({
        'professional_count': professional_count_list,
        'request_data': request_data,
        'professional_data': professional_data
    })
import tasks
import pandas as pd


def fetch_closed_service_requests(professional_id):
    data=ServiceReq.query.filter_by(professional_id=professional_id).all()
    fetched_data=[]
    for row in data:
        fetched_data.append(row)
    return fetched_data


@celery.task
def export_service_requests(closed_requests):
    # Create a DataFrame
    df = pd.DataFrame(closed_requests)
    # Define the CSV file path
    csv_file_path = os.path.join('exports', 'closed_service_requests.csv')    
    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)

    return csv_file_path  # Return the path to the CSV file

@app.route('/export/<string:professional_id>', methods=['POST'])
def export_csv(professional_id):
    closed_requests = fetch_closed_service_requests(professional_id)
    task = export_service_requests(closed_requests).apply_async()  # Trigger the async task
    return jsonify({"task_id": task.id}), 202  # Return task ID

if __name__ == "__main__":
    with app.app_context():
        tasks.schedule_task('send_scheduled_email')  # Schedule 7:30 PM IST email
        tasks.schedule_task('send_monthly_email')
    app.run(debug=True)