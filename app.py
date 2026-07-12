from flask import Flask, render_template, redirect, request
from models import db, User, Course, Registration
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create Database and Sample Data
with app.app_context():
    db.create_all()

    if Course.query.count() == 0:
        db.session.add(Course(name="Python", seats=300))
        db.session.add(Course(name="Flask", seats=200))
        db.session.commit()


# Home
@app.route('/')
def home():
    return redirect('/login')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role='student'
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            login_user(user)
            return redirect('/dashboard')

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Courses
@app.route('/courses')
@login_required
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


# Register Course
@app.route('/register_course/<int:id>')
@login_required
def register_course(id):
    course = Course.query.get(id)

    if course and course.seats > 0:
        reg = Registration(
            user_id=current_user.id,
            course_id=id
        )

        course.seats -= 1

        db.session.add(reg)
        db.session.commit()

    return redirect('/courses')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)