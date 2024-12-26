<h1 align="center"><a href="https://ultimate-planner-c321a2415a86.herokuapp.com/" target="_blank">The Ultimate Planner</a></h1> 

The Ultimate Planner is a comprehensive tool for organizing your life, breaking down big goals, and staying on track with personalized categories and progress tracking. Whether you're planning for a year, semester, or month, this intuitive platform helps you achieve more, stay motivated, and boost productivity by neatly categorizing and tracking goals in areas such as Health, Finance, and Career. Developed as Final Project of the CS50x/2024 Introduction to Computer Science at 
<br>
<a align="center" href="https://pll.harvard.edu/course/cs50-introduction-computer-science" target="_blank"><img src="static/images/docs_imgs/harvard_logo.png" heigth="25" width="100" alt="Havard Online"></a>

[**Live Demo: The Ultimate Planner**](https://ultimate-planner-c321a2415a86.herokuapp.com/)

![Alt text](static/images/docs_imgs/ultimate_planner.gif "Hero gif for Readme File")


# Contents

- [Contents](#contents)
  - [User Experience (UX)](#user-experience-ux)
    - [User Stories](#user-stories)
    - [Agile Methodologies](#agile-methodologies-with-github-kanban)
    - [Database Flowchart](#database-flowchart)
    - [Design Choices](#design-choices)
    - [Wireframes](#wireframes)
  - [Features](#features)
    - [Landing Page](#landing-page)
    - [Register](#register-page)
    - [Log In](#login-page)
    - [Dashboard](#dashboard-page)
    - [Add Category](#add-category-page)
    - [Edit Category](#edit-category-page)
    - [Add Goal](#add-goal-page)
    - [Edit Goal](#edit-goal-page)
    - [Future Features](#future-features)
  - [Marketing Strategies](#marketing-strategies)
  - [Testing](#testing)
    - [Bugs and Issues](#bugs-and-issues)
  - [Technologies Used](#technologies-used)
  - [Deployment](#deployment)
  - [Credits](#credits)
    - [Content](#content)
    - [Media](#media)
  - [Acknowledgments](#acknowledgments)
- [Thank You!](#thank-you)

___


## User Experience (UX)

### User Stories

The GitHub Kanban and Issue Tracker tools were used to manage this project effectively. You can view the board [**here**](link-to-github-kanban).

#### Epic: Goal Management
1. **As a user,** I want to create and categorize my goals (e.g., Health, Finance, Career) so that I can keep them organized and easy to track.
2. **As a user,** I want to break down my big goals into smaller milestones so that I can stay motivated and track my progress step by step.
3. **As a user,** I want to assign a timeframe (e.g., year, semester, trimester, month) to each goal so that I can plan effectively within my schedule.
4. **As a user,** I want to mark goals as "important" or "done" so that I can prioritize and see my accomplishments at a glance.
      
#### Epic: Planning and Progress Tracking
5. **As a user,** I want to track my progress visually so that I can stay motivated and measure how close I am to achieving my goals.
6. **As a user,** I want to view all my goals and milestones in a clean, intuitive interface so that I can manage them effortlessly.
7. **As a user,** I want the app to automatically save and organize my data so that I can focus on planning without worrying about losing my work.
      
#### Epic: Time Management
8. **As a user,** I want to create plans for specific timeframes (e.g., yearly, semester, trimester, monthly) so that I can adjust my focus depending on my goals.
9. **As a user,** I want to see an overview of my goals by timeframe so that I can stay on track with my plans.
  
#### Epic: Productivity and Motivation
10. **As a user,** I want to categorize my goals by life areas (e.g., personal growth, professional success) so that I can balance different aspects of my life.
11. **As a user,** I want to track both short-term and long-term goals so that I can work toward both immediate needs and future aspirations.
  
#### Epic: Onboarding and Guidance
12. **As a new user,** I want a simple and friendly introduction to the app so that I can quickly understand how to use it.

[Back to top](#contents)

---

### Agile Methodologies with GitHub Kanban

GitHub Project Boards and Kanban methodology were employed to manage tasks efficiently. By visualizing the project through "To do," "In progress," "Testing," and "Done" columns, the team maintained focus and ensured tasks moved through each stage systematically.

![Alt text](kanban-image "Kanban Board Example")

[Back to top](#contents)

---

### Database Flowchart

The database flowchart provided critical insights into the relationships between models and guided the application's development. Below is the chart created using [**dbdiagram.io**](https://dbdiagram.io/).

![Alt text](flowchart-image "Database Flowchart")

#### Explanation:
- **Primary Keys**:
  Each table has a unique primary key (user_id, category_id, goal_id).
        
- **Relationships**:
  - `Category.user_id` references `User.user_id` (1 User → N Categories).
  - `Goal.user_id` references `User.user_id` (1 User → N Goals).
  - `Goal.category_id` references `Category.category_id` (1 Category → N Goals).
         
- **Constraints**:
  Additional constraints ensure the integrity of the database. For example, fields like `user_name` and `category_name` can be defined as `unique` or `not null`.

  [Back to top](#contents)
---

### Design Choices

The app design embraces simplicity and functionality, ensuring an intuitive user experience. Transitions are smooth and visually appealing. The design leverages [**Bootstrap**](https://getbootstrap.com/) classes for consistent styling.

![Alt text](color-palette-image "Color Palette")

[Back to top](#contents)

---

### Wireframes
  - **Landing Page**:
    ![Alt text](landing-page-wf-image "landing-wf page image")

  - **Dashboard**:
    ![Alt text](dashboard-wf-image "dashboard-wf image")

   - **Add Category/Goal**:
    ![Alt text](add-wf-image "addwf image")

      [Back to top](#contents)
---

### Features
  - #### **Landing Page**
      ![Alt text](landing-page "landing-page image")

      [Back to top](#contents)

  - #### **Register Page**
      ![Alt text](register-page "register-page image")
      
      [Back to top](#contents)

  - #### **Login Page**
      ![Alt text](login-page "login-page image")
      
      [Back to top](#contents)

  - #### **Dashboard Page**
      ![Alt text](dashboard-page "dashboard-page image")
      
      [Back to top](#contents)

  - #### **Add Category Page**
      ![Alt text](add-category-page "add-category-page image")
      
      [Back to top](#contents)

  - #### **Edit Category Page**
      ![Alt text](edit-category-page "edit-category-page image")
      
      [Back to top](#contents)

  - #### **Add Goal Page**
      ![Alt text](add-goal-page "add-goal-page image")
      
      [Back to top](#contents)

  - #### **Edit Goal Page**
      ![Alt text](edit-goal-page "edit-goal-page image")
      
      [Back to top](#contents)

  ### **Future Features**
      
  [Back to top](#contents)

---

## Testing

### Bugs and Issues
While developing, some sensitive keys were accidentally pushed to GitHub. However, they were promptly regenerated and securely added as environment variables on the Heroku platform.

### Code Validation
- **HTML:** Checked via [W3C Validator](https://validator.w3.org/).
- **CSS:** Validated using [W3C CSS Validator](https://jigsaw.w3.org/css-validator/).
- **Python:** Linting performed using Flake8.

[Back to top](#contents)

---

## Deployment

### Heroku Deployment
1. Create a Heroku account if you don’t have one.
2. From the Heroku dashboard, click "New" and select "Create new app."
3. Name your app and choose a region.
4. Connect your GitHub repository.
5. Add the necessary buildpacks in the following order:
    - `heroku/python`
    - `heroku/nodejs`
6. Configure environment variables in the Heroku settings tab:
    - `PORT`: 8000
    - `DATABASE_URL`: Link to your PostgreSQL database.
    - `SECRET_KEY`: Your application’s secret key.

### GitHub Pages Deployment
1. Create a repository on GitHub.
2. Commit your code and push it to the repository.
3. Enable GitHub Pages in the repository settings.

[Back to top](#contents)

---

## Acknowledgments

By [**Cesar Garcia**](https://github.com/Cesargarciajr)


# <a href="https://pll.harvard.edu/course/cs50-introduction-computer-science" target="_blank"><img src="static/images/docs_imgs/harvard_logo.png" heigth="50" width="100" alt="Havard Online"></a> THANK YOU!

[Back to top](#contents)
