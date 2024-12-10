import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import random

if os.path.isfile("env.py"):
    import env

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ultimate_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended to disable
app.secret_key = os.environ.get("SECRET_KEY")

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model (modified to include the relationship)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # Relationship with categories
    categories = db.relationship('Category', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"

# Define the Category model with unique color
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7), nullable=False, unique=True)  # Ensure the color is unique
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Category('{self.id}', '{self.name}', '{self.color}')"


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

@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    categories = user.categories  # Get the categories associated with the user

    if request.method == 'POST':
        category_name = request.form['category_name'].strip()  # Trim leading/trailing spaces
        formatted_name = ' '.join(word.capitalize() for word in category_name.split())  # Capitalize each word
        user_id = session['user_id']

        # Check for uniqueness of category name for the user
        if Category.query.filter_by(name=formatted_name, user_id=user_id).first():
            flash("Category already exists. Try another name", "danger")
            return redirect(url_for('add_category'))

        # Generate a random hex color and ensure it is unique
        def generate_unique_color():
            color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if Category.query.filter_by(color=color).first():
                return generate_unique_color()  # Recursively call the function to generate a new color
            return color

        category_color = generate_unique_color()

        # Create and add the new category with the formatted name and unique color
        new_category = Category(name=formatted_name, color=category_color, user_id=user_id)
        db.session.add(new_category)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_category.html', categories=categories)

@app.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    # Fetch the category by ID and ensure it belongs to the logged-in user
    category = Category.query.filter_by(id=category_id, user_id=session['user_id']).first()
    if not category:
        flash("Category not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        category_name = request.form['category_name'].strip()
        category_color = request.form['category_color']

        # Ensure the name is unique
        formatted_name = ' '.join(word.capitalize() for word in category_name.split())
        existing_category = Category.query.filter_by(name=formatted_name, user_id=session['user_id']).first()
        if existing_category and existing_category.id != category.id:
            flash("Category name already exists, please try another name.", "danger")
            return redirect(url_for('edit_category', category_id=category.id))

        # Ensure the color is unique
        color_taken = Category.query.filter_by(color=category_color, user_id=session['user_id']).first()
        if color_taken and color_taken.id != category.id:
            flash("This color is already used by another category. Please select a different color.", "danger")
            return redirect(url_for('edit_category', category_id=category.id))

        # Update category details
        category.name = formatted_name
        category.color = category_color
        db.session.commit()

        flash("Category updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_category.html', category=category)


@app.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    # Fetch the category and verify ownership
    category = Category.query.filter_by(id=category_id, user_id=session['user_id']).first()
    if not category:
        flash("Category not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    # Delete the category
    db.session.delete(category)
    db.session.commit()

    flash("Category deleted successfully.", "success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
