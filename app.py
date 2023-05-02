from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import pandas as pd
import matplotlib.pyplot as plt
import mpld3

current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

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
    chart_filename = db.Column(db.String(300), unique=True)

    def __init__(self, filename, chart_filename):
        self.filename = filename
        self.chart_filename = chart_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    html_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html') and f.startswith(current_user.username)]
    return render_template('dashboard.html', name=current_user.username, html_files=html_files)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        username = current_user.username
        new_filename = f"{username}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        flash('File uploaded successfully!', 'success')
        # Create charts from uploaded file
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()

            if file_extension == 'csv':
                df = pd.read_csv(file_path)
            elif file_extension == 'xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_extension == 'xls':
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                raise ValueError(f"Unsupported file extension: {file_extension}")

            charts = []
            for i, column in enumerate(df.columns):
                chart_filename = f"{current_user.username}_{os.path.splitext(filename)[0]}_{i+1}.html"
                
                # Create a figure with three subplots (scatter, bar, and pie)
                fig, (ax_scatter, ax_bar, ax_pie) = plt.subplots(1, 3, figsize=(18, 4))
                fig.suptitle(column)

                # Scatter plot
                ax_scatter.set_title(column)
                ax_scatter.scatter(range(len(df[column])), df[column])

                # Bar plot
                ax_bar.set_title(column)
                ax_bar.bar(range(len(df[column])), df[column])

                # Pie chart
                ax_pie.set_title(column)
                # You may want to modify the following line to aggregate the data in a meaningful way for a pie chart
                pie_data = df[column].value_counts(normalize=True)
                ax_pie.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
                ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

                plt.tight_layout()  # Adjust layout to prevent overlapping labels

                # Save the combined figure as an HTML file
                html = mpld3.fig_to_html(fig)
                chart_file = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
                with open(chart_file, 'w') as f:
                    f.write(html)
                
                # Create an ExcelFile object and add it to the database
                chart = ExcelFile(filename=filename, chart_filename=chart_filename)
                db.session.add(chart)
                charts.append(chart)

            db.session.commit()  # Save the changes to the database
        except Exception as e:
            flash(f'Failed to create charts: {e}', 'danger')
            return redirect(url_for('dashboard'))
    
    # Display charts in a new page
    return render_template('charts.html', charts=charts)


@app.route('/charts', methods=['GET', 'POST'])
@login_required
def charts():
    html_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.html')]
    return render_template('dashboard.html', name=current_user.username, html_files=html_files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
