from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'njdskgvhdx,csbdxhchcvdhcx'


login_manager = LoginManager()
login_manager.init_app(app)


# Load a user from the database by their ID
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB
class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
 
with app.app_context():
    db.create_all()






@app.route('/')
def home():
    return render_template("index.html")



@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        # Check whether the email already exists
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalars().first()

        if user:
            flash("This email is already registered.", "error")
            return redirect(url_for('register'))

        # Generate a hashed password
        pwhashed = generate_password_hash(
            password=password,
            method='pbkdf2:sha256',
            salt_length=16
        )

        # Create and save the new user
        new_user = User(
            email=email,
            password=pwhashed,
            name=name
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")



@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
        if user and user.email == email and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('secrets'))
        else:
            flash("Invalid email or password. Please try again.", "error")
        
    return render_template("login.html")


@app.route('/secrets', methods=["GET", "POST"])
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    load_user(current_user.get_id())
    logout_user()
    return redirect(url_for('login'))


@app.route('/download', methods=["GET"])
def download():
    return send_from_directory(
        directory='static/files',
        path='cheat_sheet.pdf',
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
