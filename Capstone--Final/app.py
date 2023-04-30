from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
import mpld3
import os
import pandas as pd
import matplotlib.pyplot as plt
import app
import uuid

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')  # Change this to the directory where you want to store uploaded files

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}  # Change this to the set of file extensions you want to allow

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class ExcelFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), unique=True)

    def __init__(self, filename):
        self.filename = filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'C:\\Users\\risha\\OneDrive\\Desktop\\test\\uploads'

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'} 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    html_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]
    return render_template('dashboard.html', name=current_user.username, html_files=html_files)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


class ExcelFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), unique=True)
    chart_filename = db.Column(db.String(300), unique=True)

    def __init__(self, filename, chart_filename):
        self.filename = filename
        self.chart_filename = chart_filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File uploaded successfully!', 'success')

        # Create charts from uploaded file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            charts = []
            for column in df.columns:
                chart_id = str(uuid.uuid4())
                chart_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{chart_id}.html')
                fig, ax = plt.subplots()
                ax.set_title(column)
                ax.plot(df[column])
                html = mpld3.fig_to_html(fig)
                with open(chart_file, 'w') as f:
                    f.write(html)
                # Create an ExcelFile object and add it to the database
                chart = ExcelFile(filename=filename, chart_filename=f'{chart_id}.html')
                db.session.add(chart)
                charts.append(chart)
            db.session.commit()  # Save the changes to the database
        except Exception as e:
            flash(f'Failed to create charts: {e}', 'danger')
            return redirect(url_for('dashboard'))

        # Display charts in a new page
        return render_template('charts.html', charts=charts)
    return redirect(url_for('charts'))

@app.route('/charts')
@login_required
def charts():
    html_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]
    return render_template('charts.html', name=current_user.username, html_files=html_files)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)