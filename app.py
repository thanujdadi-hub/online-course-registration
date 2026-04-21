from flask import Flask, render_template, redirect, request
from models import db, User, Course, Registration
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect('/login')


# 🔐 Register
@app.route('/register', methods=['GET','POST'])
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


# 🔐 Login
@app.route('/login', methods=['GET','POST'])
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


# 🏠 Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# 📚 View Courses
@app.route('/courses')
@login_required
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


# ✅ Register for Course
@app.route('/register_course/<int:id>')
@login_required
def register_course(id):
    course = Course.query.get(id)

    if course.seats > 0:
        reg = Registration(user_id=current_user.id, course_id=id)
        course.seats -= 1

        db.session.add(reg)
        db.session.commit()

    return redirect('/courses')


# 🚪 Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# 🛠️ Create DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add sample courses (only first time)
        if Course.query.count() == 0:
            db.session.add(Course(name="Python", seats=300))
            db.session.add(Course(name="Flask", seats=200))
            db.session.commit()

    app.run(debug=True)