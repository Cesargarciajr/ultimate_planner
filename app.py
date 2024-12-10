from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ultimate_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

# Initialize the database
db = SQLAlchemy(app)

# Define the User model (modified to include the relationship)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # Relationship with categories
    categories = db.relationship('Category', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"

# Define the Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Category('{self.id}', '{self.name}')"


# Create the database and tables (run this only once, e.g., manually or in setup)
def create_db():
    with app.app_context():
        db.create_all()

# Define route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query the user from the database
        user = User.query.filter_by(username=username).first()

        # Validate user credentials
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

# Define route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if passwords match
        if password != confirmation:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # Hash the password and add the user to the database
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# Define route for the dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username, categories=user.categories)

# Define route for the logout page
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Define route for the home page
@app.route("/")
def home():
    """Home template running"""
    return render_template("base.html")

# Define route to add a category
@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        category_name = request.form['category_name']
        user_id = session['user_id']  # Assuming user_id is stored in session on login

        # Create and add the category
        new_category = Category(name=category_name, user_id=user_id)
        db.session.add(new_category)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_category.html')  # Template for adding categories

if __name__ == '__main__':
    app.run(debug=True)
