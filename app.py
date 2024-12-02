from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Set the URI for your SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ultimate_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended to disable

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"


# Define route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    return render_template("login.html")

# Route to register new user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    return render_template("register.html")

@app.route("/")
def home():
    """Home template running"""
    return render_template("base.html")

if __name__ == '__main__':
    app.run(debug=True)
