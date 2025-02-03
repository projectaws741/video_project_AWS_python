from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# AWS SSM Client
ssm_client = boto3.client('ssm', region_name='us-east-1')  # Change to your AWS region

def get_parameter(name, decrypt=True):
    """Fetch parameter value from AWS SSM Parameter Store."""
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=decrypt)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None

# Fetch sensitive values from AWS SSM Parameter Store
#app.secret_key = get_parameter('/lms/secret_key')
DATABASE_URI = get_parameter('/lms/db_uri')
AWS_ACCESS_KEY = get_parameter('/lms/aws_access_key')
AWS_SECRET_KEY = get_parameter('/lms/aws_secret_key')
S3_BUCKET = get_parameter('/lms/s3_bucket')

# Flask Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# AWS S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/view_videos')
@login_required
def view_videos():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        videos = [
            {
                'name': obj['Key'],
                'url': s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET, 'Key': obj['Key']},
                    ExpiresIn=3600  # URL valid for 1 hour
                )
            }
            for obj in response.get('Contents', [])
        ]
        return render_template('view_videos.html', videos=videos)
    except NoCredentialsError:
        flash('AWS credentials not found.')
        return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                s3_client.upload_fileobj(file, S3_BUCKET, file.filename)
                flash('Video uploaded successfully!')
            except NoCredentialsError:
                flash('AWS credentials not found.')
        return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

