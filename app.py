from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '5e26204d37b02e417e10ea7a306bc5aa8312389c508f0579b47223a5dd36df98'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://krishna:KrishnaKittu123@terraform-20250125022323863700000001.cdogag6ced24.us-east-1.rds.amazonaws.com:5432/video_upload_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# AWS S3 Configuration
s3 = boto3.client('s3')
S3_BUCKET = "lmsprojectvideos"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class UploadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    video_name = db.Column(db.String(120), nullable=False)

class DownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    video_name = db.Column(db.String(120), nullable=False)

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "User already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Upload to S3
            s3.upload_file(file_path, S3_BUCKET, filename)

            # Record upload in DB
            new_upload = UploadRecord(username=session['username'], video_name=filename)
            db.session.add(new_upload)
            db.session.commit()

            os.remove(file_path)
            return "Video uploaded successfully!"
    return render_template('upload.html')

@app.route('/view')
def view():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch all videos from S3
    videos = s3.list_objects_v2(Bucket=S3_BUCKET).get('Contents', [])
    return render_template('view.html', videos=[video['Key'] for video in videos])

@app.route('/download/<video_name>')
def download(video_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(UPLOAD_FOLDER, video_name)
    s3.download_file(S3_BUCKET, video_name, file_path)

    # Record download in DB
    new_download = DownloadRecord(username=session['username'], video_name=video_name)
    db.session.add(new_download)
    db.session.commit()

    return redirect(url_for('view'))

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5000)
