import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import random

if os.path.isfile("env.py"):
    import env

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ultimate_planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended to disable
app.secret_key = os.environ.get("SECRET_KEY")

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model (modified to include the relationship)
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # Relationship with categories
    categories = db.relationship('Category', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.user_id}', '{self.user_name}')"

# Define the Category model with unique color
class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_color = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('category_name', 'user_id', name='unique_category_per_user'),
        db.UniqueConstraint('category_color', 'user_id', name='unique_color_per_user')
    )

    def __repr__(self):
        return f"Category('{self.category_id}', '{self.category_name}', '{self.category_color}')"

# Define allowed timeframes for goals
ALLOWED_TIMEFRAMES = ['year', 'semester', 'trimester', 'month']

# Define the Goal model
class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(100), nullable=False)
    goal_description = db.Column(db.String(255), nullable=False)
    goal_important = db.Column(db.Boolean, default=False)
    goal_done = db.Column(db.Boolean, default=False)
    goal_timeframe_selection = db.Column(db.String(50), nullable=False)  # Use a regular string column
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    def __repr__(self):
        return f"Goal('{self.goal_id}', '{self.goal_name}', '{self.goal_description}', '{self.goal_important}', '{self.goal_done}', '{self.goal_timeframe_selection}')"

# Create the database and tables (run this only once, e.g., manually or in setup)
def create_db():
    with app.app_context():
        db.create_all()

# Define route for the home page
@app.route("/")
def index():
    """Home template running"""
    return render_template("index.html")

# Define route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if passwords match
        if password != confirmation:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        # Check if username already exists
        if User.query.filter_by(user_name=user_name).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # Hash the password and add the user to the database
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(user_name=user_name, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# Define route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")

        # Query the user from the database
        user = User.query.filter_by(user_name=user_name).first()

        # Validate user credentials
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['user_name'] = user.user_name
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

# Define route for the logout page
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Define route for the dashboard page
@app.route('/dashboard')
def dashboard():
    """Dashboard page with user's categories and goals"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    categories = user.categories
    goals = Goal.query.filter_by(user_id=user.user_id).all()

    # Debugging statements
    print("User ID:", user.user_id)
    print("Categories:", categories)
    print("Goals:", goals)
    for goal in goals:
        print("Goal ID:", goal.goal_id)
        print("Goal Timeframe Selection:", goal.goal_timeframe_selection)

    return render_template('dashboard.html', username=user.user_name, categories=categories, goals=goals)

# Define route for the add category page
@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
    """Add a new category"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    categories = user.categories  # Categories associated with the current user

    if request.method == 'POST':
        category_name = request.form['category_name'].strip()  # Trim spaces
        formatted_name = ' '.join(word.capitalize() for word in category_name.split())  # Capitalize each word
        user_id = session['user_id']

        # Check if the user already has this category name
        existing_category = Category.query.filter_by(category_name=formatted_name, user_id=user_id).first()
        if existing_category:
            flash("Category with this name already exists in your list.", "danger")
            return redirect(url_for('add_category'))

        # Generate a unique color
        def generate_unique_color():
            color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if Category.query.filter_by(category_color=color, user_id=user_id).first():
                return generate_unique_color()  # Recursively call to generate another color
            return color

        category_color = generate_unique_color()

        # Check if the user already has this category color
        existing_color_category = Category.query.filter_by(category_color=category_color, user_id=user_id).first()
        if existing_color_category:
            flash("Category with this color already exists in your list.", "danger")
            return redirect(url_for('add_category'))

        # Add the new category
        new_category = Category(category_name=formatted_name, category_color=category_color, user_id=user_id)
        db.session.add(new_category)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_category.html', categories=categories)

# Define route for the edit category page
@app.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    """Edit an existing category"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    # Fetch the category by ID and ensure it belongs to the logged-in user
    category = Category.query.filter_by(category_id=category_id, user_id=session['user_id']).first()
    if not category:
        flash("Category not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        category_name = request.form['category_name'].strip()
        category_color = request.form['category_color']

        # Ensure the name is unique
        formatted_name = ' '.join(word.capitalize() for word in category_name.split())
        existing_category = Category.query.filter_by(category_name=formatted_name, user_id=session['user_id']).first()
        if existing_category and existing_category.category_id != category.category_id:
            flash("Category name already exists, please try another name.", "danger")
            return redirect(url_for('edit_category', category_id=category.category_id))

        # Ensure the color is unique
        color_taken = Category.query.filter_by(category_color=category_color, user_id=session['user_id']).first()
        if color_taken and color_taken.category_id != category.category_id:
            flash("This color is already used by another category. Please select a different color.", "danger")
            return redirect(url_for('edit_category', category_id=category.category_id))

        # Update category details
        category.category_name = formatted_name
        category.category_color = category_color
        db.session.commit()

        flash("Category updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_category.html', category=category)

# Define route for the delete category page
@app.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """Delete an existing category"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    # Fetch the category and verify ownership
    category = Category.query.filter_by(category_id=category_id, user_id=session['user_id']).first()
    if not category:
        flash("Category not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    # Delete the category
    db.session.delete(category)
    db.session.commit()

    flash("Category deleted successfully.", "success")
    return redirect(url_for('dashboard'))

# Define route for the add goal page
@app.route('/add-goal', methods=['GET', 'POST'])
def add_goal():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    categories = user.categories

    if request.method == 'POST':
        goal_name = request.form['goal_name'].strip()
        formatted_name = ' '.join(word.capitalize() for word in goal_name.split())
        category_id = request.form['category_id']
        goal_description = request.form['goal_description'].strip()
        goal_important = 'goal_important' in request.form
        goal_done = 'goal_done' in request.form
        goal_timeframe_selection = request.form['goal_timeframe_selection'].lower()

        # Validate the timeframe selection
        if goal_timeframe_selection not in ALLOWED_TIMEFRAMES:
            flash("Invalid timeframe selection.", "danger")
            return redirect(url_for('add_goal'))

        # Validate that a valid category is selected
        category = Category.query.get(category_id)
        if not category or category.user_id != user.user_id:
            flash("Invalid category selected.", "danger")
            return redirect(url_for('add_goal'))

        # Check if a goal with the same name already exists for the user under this category and time period
        existing_goal = Goal.query.filter_by(goal_name=formatted_name, user_id=user.user_id, category_id=category_id, goal_timeframe_selection=goal_timeframe_selection).first()
        if existing_goal:
            flash("Goal with this name already exists in this category and time period.", "danger")
            return redirect(url_for('add_goal'))

        # Create and add the new goal
        new_goal = Goal(
            user_id=user.user_id,
            category_id=category_id,
            goal_name=formatted_name,
            goal_description=goal_description,
            goal_important=goal_important,
            goal_done=goal_done,
            goal_timeframe_selection=goal_timeframe_selection
        )
        db.session.add(new_goal)
        db.session.commit()

        flash("Goal created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_goal.html', categories=categories)

# Define route for the edit goal page
@app.route('/edit-goal/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    """Edit an existing goal"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.user_id:
        flash("You do not have permission to edit this goal.", "danger")
        return redirect(url_for('dashboard'))

    categories = user.categories  # Get the categories associated with the user

    if request.method == 'POST':
        goal_name = request.form['goal_name'].strip()  # Trim leading/trailing spaces
        formatted_name = ' '.join(word.capitalize() for word in goal_name.split())  # Capitalize each word
        category_id = request.form['category_id']
        goal_description = request.form['goal_description'].strip()
        goal_important = 'goal_important' in request.form  # Checkbox will be in the form as 'goal_important'
        goal_done = 'goal_done' in request.form  # Checkbox will be in the form as 'goal_done'
        
        # Time slot value from the form, ensure it's lowercased
        goal_timeframe_selection = request.form['goal_timeframe_selection'].lower()  # Convert to lowercase
        
        # Validate that a valid category is selected
        category = Category.query.get(category_id)
        if not category or category.user_id != user.user_id:
            flash("Invalid category selected.", "danger")
            return redirect(url_for('edit_goal', goal_id=goal_id))

        # Check if a goal with the same name already exists for the user under this category
        existing_goal = Goal.query.filter_by(goal_name=formatted_name, user_id=user.user_id, category_id=category_id).first()
        if existing_goal and existing_goal.goal_id != goal_id:
            flash("Goal with this name already exists in this category.", "danger")
            return redirect(url_for('edit_goal', goal_id=goal_id))

        # Update the goal
        goal.goal_name = formatted_name
        goal.category_id = category_id
        goal.goal_description = goal_description
        goal.goal_important = goal_important
        goal.goal_done = goal_done
        goal.goal_timeframe_selection = goal_timeframe_selection  # Directly assign the lowercase value

        db.session.commit()

        flash("Goal updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_goal.html', goal=goal, categories=categories)

# Define route for the delete goal page
@app.route('/delete-goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    """Delete an existing goal"""
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.user_id:
        flash("You do not have permission to delete this goal.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(goal)
    db.session.commit()

    flash("Goal deleted successfully.", "success")
    return redirect(url_for('dashboard'))

# Define route for marking a goal as done
@app.route('/mark-done/<int:goal_id>', methods=['POST'])
def mark_done(goal_id):
    """ Mark a goal as done """
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.user_id:
        flash("You do not have permission to modify this goal.", "danger")
        return redirect(url_for('dashboard'))

    # Toggle the done status
    goal.goal_done = not goal.goal_done
    db.session.commit()

    flash("Goal status updated.", "success")
    return redirect(url_for('dashboard'))

# Define route for marking a goal as important
@app.route('/mark-important/<int:goal_id>', methods=['POST'])
def mark_important(goal_id):
    """ Mark a goal as important """
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.user_id:
        flash("You do not have permission to modify this goal.", "danger")
        return redirect(url_for('dashboard'))

    # Toggle the important status
    goal.goal_important = not goal.goal_important
    db.session.commit()

    flash("Goal status updated.", "success")
    return redirect(url_for('dashboard'))

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)