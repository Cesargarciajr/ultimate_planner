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

    # If the request method is POST, process the registration form
    if request.method == "POST":
        # Retrieve form inputs
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input fields
        if not username:
            flash("Must provide username", "error")
            return redirect("/register")
        if not password:
            flash("Must provide password", "error")
            return redirect("/register")
        if not confirmation:
            flash("Must confirm password", "error")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords do not match", "error")
            return redirect("/register")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Attempt to insert the new user into the database using SQLAlchemy
        try:
            new_user = User(username=username, hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect("/login")
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f"An error occurred: {e}", "error")

    # If the request method is GET, render the registration form
    return render_template("register.html")

@app.route("/")
def home():
    """Home template running"""
    return render_template("base.html")

if __name__ == '__main__':
    app.run(debug=True)
