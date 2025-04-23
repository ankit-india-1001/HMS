from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # 'admin' or 'doctor'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    condition = db.Column(db.String(200))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))

    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/access')
def access_portal():
    return render_template('user_access.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return "Username already exists"
        
        # Add new user with selected role
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')  # Redirect to login page after successful registration
    return render_template('register.html')




@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user'] = user.username
        session['role'] = user.role
        return redirect('/dashboard')
    return "Invalid credentials"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    if session['role'] == 'admin':
        return render_template('index.html')
    elif session['role'] == 'doctor':
        return redirect('/appointments')
    elif session['role'] == 'user':
        return redirect('/access')
    return "Unknown role"

@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = request.form['name']
    age = request.form['age']
    condition = request.form['condition']
    db.session.add(Patient(name=name, age=age, condition=condition))
    db.session.commit()
    return redirect(url_for('view_patients'))

@app.route('/patients')
def view_patients():
    if 'user' not in session:
        return redirect('/')
    query = request.args.get('query', '')
    if query:
        patients = Patient.query.filter(
            (Patient.name.contains(query)) | 
            (Patient.condition.contains(query))
        ).all()
    else:
        patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        db.session.add(Doctor(name=name))
        db.session.commit()
        return redirect('/dashboard')
    return render_template('add_doctor.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'role' not in session or session['role'] not in ['admin', 'user']:
        return redirect('/')
        
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    
    if request.method == 'POST':
        patient_id = request.form['patient']
        doctor_id = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        appt = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, time=time)
        db.session.add(appt)
        db.session.commit()
        return redirect('/appointments')
        
    return render_template('book_appointment.html', patients=patients, doctors=doctors)


@app.route('/appointments')
def view_appointments():
    if 'role' not in session:
        return redirect('/')
    if session['role'] == 'admin':
        appts = Appointment.query.all()
    elif session['role'] == 'doctor':
        appts = Appointment.query.all()
    else:
        doctor = Doctor.query.filter_by(name=session['user']).first()
        appts = Appointment.query.filter_by(doctor_id=doctor.id).all() if doctor else []
    return render_template('appointments.html', appointments=appts)



#Add a default admin user if none exists
with app.app_context():
    db.create_all()

    # Check if the admin user exists
    if not User.query.filter_by(username='admin').first():  # Check for existing user
        # If the admin user does not exist, create one
        default_user = User(username='admin', password='admin123', role='admin')
        db.session.add(default_user)
        db.session.commit()
        print("Default admin user created!")


if __name__ == '__main__':
    app.run()

from app import db
with app.app_context():
    db.create_all()

# with app.app_context():
#     if not User.query.filter_by(username='admin').first():
#         db.session.add(User(username='admin', password='admin123', role='admin'))
#     if not User.query.filter_by(username='doc1').first():
#         db.session.add(User(username='doc1', password='doc123', role='doctor'))
#     db.session.commit()



#########NEW

# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
# app.config['SECRET_KEY'] = 'your_secret_key'
# db = SQLAlchemy(app)

# # Models
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True)
#     password = db.Column(db.String(100))
#     role = db.Column(db.String(20))  # 'admin' or 'doctor'

# class Patient(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     age = db.Column(db.Integer)
#     condition = db.Column(db.String(200))

# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))

# class Appointment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
#     doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
#     date = db.Column(db.String(20))
#     time = db.Column(db.String(20))

#     patient = db.relationship('Patient', backref='appointments')
#     doctor = db.relationship('Doctor', backref='appointments')

# # Routes
# @app.route('/')
# def login():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def do_login():
#     username = request.form['username']
#     password = request.form['password']
#     user = User.query.filter_by(username=username, password=password).first()
#     if user:
#         session['user'] = user.username
#         session['role'] = user.role
#         return redirect('/dashboard')
#     return "Invalid credentials"

# @app.route('/dashboard')
# def dashboard():
#     if 'user' not in session:
#         return redirect('/')
#     if session['role'] == 'admin':
#         return render_template('index.html')
#     elif session['role'] == 'doctor':
#         return redirect('/appointments')
#     return "Unknown role"

# @app.route('/add_patient', methods=['POST'])
# def add_patient():
#     name = request.form['name']
#     age = request.form['age']
#     condition = request.form['condition']
#     db.session.add(Patient(name=name, age=age, condition=condition))
#     db.session.commit()
#     return redirect(url_for('view_patients'))

# @app.route('/patients')
# def view_patients():
#     if 'user' not in session:
#         return redirect('/')
#     query = request.args.get('query', '')
#     if query:
#         patients = Patient.query.filter(
#             (Patient.name.contains(query)) | 
#             (Patient.condition.contains(query))
#         ).all()
#     else:
#         patients = Patient.query.all()
#     return render_template('patients.html', patients=patients)

# @app.route('/add_doctor', methods=['GET', 'POST'])
# def add_doctor():
#     if 'role' not in session or session['role'] != 'admin':
#         return redirect('/')
#     if request.method == 'POST':
#         name = request.form['name']
#         db.session.add(Doctor(name=name))
#         db.session.commit()
#         return redirect('/dashboard')
#     return render_template('add_doctor.html')

# @app.route('/book_appointment', methods=['GET', 'POST'])
# def book_appointment():
#     if 'role' not in session or session['role'] != 'admin':
#         return redirect('/')
#     patients = Patient.query.all()
#     doctors = Doctor.query.all()
#     if request.method == 'POST':
#         patient_id = request.form['patient']
#         doctor_id = request.form['doctor']
#         date = request.form['date']
#         time = request.form['time']
#         appt = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, time=time)
#         db.session.add(appt)
#         db.session.commit()
#         return redirect('/appointments')
#     return render_template('book_appointment.html', patients=patients, doctors=doctors)

# @app.route('/appointments')
# def view_appointments():
#     if 'role' not in session:
#         return redirect('/')
#     if session['role'] == 'admin':
#         appts = Appointment.query.all()
#     else:
#         doctor = Doctor.query.filter_by(name=session['user']).first()
#         appts = Appointment.query.filter_by(doctor_id=doctor.id).all() if doctor else []
#     return render_template('appointments.html', appointments=appts)

# # Add a default admin user if none exists
# with app.app_context():
#     db.create_all()

#     # Check if the admin user exists
#     if not User.query.filter_by(username='admin').first():  # Check for existing user
#         # If the admin user does not exist, create one
#         default_user = User(username='admin', password='admin123', role='admin')
#         db.session.add(default_user)
#         db.session.commit()
#         print("Default admin user created!")

# if __name__ == '__main__':
#     app.run(debug=True)

