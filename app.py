import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from sqlalchemy import Enum
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
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='unique_category_per_user'),
        db.UniqueConstraint('color', 'user_id', name='unique_color_per_user')
    )

    def __repr__(self):
        return f"Category('{self.id}', '{self.name}', '{self.color}')"

    
# Define the Goal model
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID as primary key
    
    # Foreign key linking to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='goals', lazy=True)
    
    # Name of the goal
    name = db.Column(db.String(100), nullable=False)
    
    # Foreign key linking to Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref='goals', lazy=True)
    
    # Description text for the goal
    text = db.Column(db.Text, nullable=False)
    
    # Important and Done toggles
    important = db.Column(db.Boolean, default=False, nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    
    # Enum for time slot
    class TimeSlotEnum(PyEnum):
        YEAR = 'year'
        SEMESTER = 'semester'
        TRIMESTER = 'trimester'
        MONTH = 'month'
    
    time_slot = db.Column(Enum(TimeSlotEnum), nullable=False, default=TimeSlotEnum.MONTH)

    def __repr__(self):
        return (f"Goal('{self.id}', '{self.name}', UserID: '{self.user_id}', "
                f"CategoryID: '{self.category_id}', Important: {self.important}, "
                f"Done: {self.done}, TimeSlot: {self.time_slot.value})")


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
    goals = user.goals  # Retrieves the goals related to the logged-in user
    return render_template('dashboard.html', username=user.username, categories=user.categories, goals=goals)

# Define route for the logout page
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Define route for the home page
@app.route("/")
def index():
    """Home template running"""
    return render_template("index.html")


@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
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
        existing_category = Category.query.filter_by(name=formatted_name, user_id=user_id).first()
        if existing_category:
            flash("Category with this name already exists in your list.", "danger")
            return redirect(url_for('add_category'))

        # Generate a unique color
        def generate_unique_color():
            color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if Category.query.filter_by(color=color, user_id=user_id).first():
                return generate_unique_color()  # Recursively call to generate another color
            return color

        category_color = generate_unique_color()

        # Check if the user already has this category color
        existing_color_category = Category.query.filter_by(color=category_color, user_id=user_id).first()
        if existing_color_category:
            flash("Category with this color already exists in your list.", "danger")
            return redirect(url_for('add_category'))

        # Add the new category
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


@app.route('/add-goal', methods=['GET', 'POST'])
def add_goal():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    categories = user.categories  # Get the categories associated with the user

    if request.method == 'POST':
        goal_name = request.form['goal_name'].strip()  # Trim leading/trailing spaces
        formatted_name = ' '.join(word.capitalize() for word in goal_name.split())  # Capitalize each word
        category_id = request.form['category_id']
        goal_text = request.form['goal_text'].strip()
        important = 'important' in request.form  # Checkbox will be in the form as 'important'
        done = 'done' in request.form  # Checkbox will be in the form as 'done'
        
        # Time slot value from the form, ensure it's uppercased
        time_slot = request.form['time_slot'].upper()  # Convert to uppercase
        
        # Validate that a valid category is selected
        category = Category.query.get(category_id)
        if not category or category.user_id != user.id:
            flash("Invalid category selected.", "danger")
            return redirect(url_for('add_goal'))

        # Check if a goal with the same name already exists for the user under this category
        if Goal.query.filter_by(name=formatted_name, user_id=user.id, category_id=category_id).first():
            flash("Goal with this name already exists in this category.", "danger")
            return redirect(url_for('add_goal'))

        # Create and add the new goal
        new_goal = Goal(
            user_id=user.id,
            category_id=category_id,
            name=formatted_name,
            text=goal_text,
            important=important,
            done=done,
            time_slot=time_slot  # This will now be passed in uppercase
        )
        db.session.add(new_goal)
        db.session.commit()

        flash("Goal created successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_goal.html', categories=categories)


@app.route('/edit-goal/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.id:
        flash("You do not have permission to edit this goal.", "danger")
        return redirect(url_for('dashboard'))

    categories = user.categories  # Get the categories associated with the user

    if request.method == 'POST':
        goal_name = request.form['goal_name'].strip()  # Trim leading/trailing spaces
        formatted_name = ' '.join(word.capitalize() for word in goal_name.split())  # Capitalize each word
        category_id = request.form['category_id']
        goal_text = request.form['goal_text'].strip()
        important = 'important' in request.form  # Checkbox will be in the form as 'important'
        done = 'done' in request.form  # Checkbox will be in the form as 'done'
        
        # Time slot value from the form, ensure it's uppercased
        time_slot = request.form['time_slot'].upper()  # Convert to uppercase
        
        # Validate that a valid category is selected
        category = Category.query.get(category_id)
        if not category or category.user_id != user.id:
            flash("Invalid category selected.", "danger")
            return redirect(url_for('edit_goal', goal_id=goal_id))

        # Check if a goal with the same name already exists for the user under this category
        existing_goal = Goal.query.filter_by(name=formatted_name, user_id=user.id, category_id=category_id).first()
        if existing_goal and existing_goal.id != goal_id:
            flash("Goal with this name already exists in this category.", "danger")
            return redirect(url_for('edit_goal', goal_id=goal_id))

        # Update the goal
        goal.name = formatted_name
        goal.category_id = category_id
        goal.text = goal_text
        goal.important = important
        goal.done = done
        goal.time_slot = Goal.TimeSlotEnum[time_slot]

        db.session.commit()

        flash("Goal updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_goal.html', goal=goal, categories=categories)


@app.route('/delete-goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.id:
        flash("You do not have permission to delete this goal.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(goal)
    db.session.commit()

    flash("Goal deleted successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/mark-done/<int:goal_id>', methods=['POST'])
def mark_done(goal_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.id:
        flash("You do not have permission to modify this goal.", "danger")
        return redirect(url_for('dashboard'))

    # Toggle the done status
    goal.done = not goal.done
    db.session.commit()

    flash("Goal status updated.", "success")
    return redirect(url_for('dashboard'))

@app.route('/mark-important/<int:goal_id>', methods=['POST'])
def mark_important(goal_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Get the logged-in user
    goal = Goal.query.get_or_404(goal_id)  # Get the goal or return 404 if not found

    # Ensure the goal belongs to the logged-in user
    if goal.user_id != user.id:
        flash("You do not have permission to modify this goal.", "danger")
        return redirect(url_for('dashboard'))

    # Toggle the important status
    goal.important = not goal.important
    db.session.commit()

    flash("Goal status updated.", "success")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
