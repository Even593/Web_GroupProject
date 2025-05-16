# FitTrack — Web-based Fitness Tracker

## 1. Purpose and Design

**FitTrack** is a lightweight web-based fitness tracking platform that enables users to manage and analyze their personal workout records. The key design goals are simplicity, user control, and secure data handling.

### Core Features:
- **User Account System** with secure login, password hashing, and CSRF protection  
- **Workout Records**: Track date, duration, calories, and personal notes  
- **Analytics Dashboard**: Visualize trends, such as total time, best 5k, longest distance, and calories burned  
- **Workout Sharing**: Selectively share workout records with other registered users  
- **Profile Page**: Display user information including username, gender, birthdate  
- **PDF Export Support** for weight tracking logs  
- **Mutual Friend System**: Add and remove friends with mutual following (like Strava)  
- **Private Messaging**: Send and receive private messages between friends  
- **Friends' Workout Feed (Circle)**: View all workout records from mutual friends, similar to a social feed  
- **Comments and Likes**: Comment on and like friends' workout records  
- **Backend Design** using modular Flask Blueprints, SQLAlchemy models, and utility wrappers for security  

The application uses:
- **Flask** (backend framework)  
- **Flask-WTF** for form handling & CSRF protection  
- **Jinja2** templating engine  
- **SQLAlchemy** ORM  
- **Chart.js** for analytics visualization  
- **Bootstrap 5** for UI components  

---

## 2. Group Members

| Name         | UWA ID     | GitHub Username                                      |
|--------------|------------|------------------------------------------------------|
| Leo Yuan     | 23998001   | [@LeoYuan0225](https://github.com/LeoYuan0225)       |
| Junyu Zhang  | 24368182   | [@fish47](https://github.com/fish47)                 |
| Yifan Lu     | 24094198   | [@Even593](https://github.com/Even593)               |
| XI Qin       | 24235608   | [@xiqin2049](https://github.com/xiqin2049)           |

🔗 GitHub Repository (Private): [https://github.com/Even593/Web_GroupProject](https://github.com/Even593/Web_GroupProject)

---

## 3. How to Launch the Application

### Step 1 – Clone the repository

```bash
git clone https://github.com/Even593/Web_GroupProject.git
cd Web_GroupProject
```

### Step 2 – Create and activate a virtual environment

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (CMD):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3 – Install dependencies

Install the required Python packages:

```bash
pip install flask flask-sqlalchemy flask-wtf
```

Alternatively, if you have a `requirements.txt` file, run:

```bash
pip install -r requirements.txt
```

### Step 4 – Set environment variables and launch the application

**macOS/Linux:**

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

**Windows (CMD):**

```bash
set FLASK_APP=app
set FLASK_ENV=development
flask run
```

Once the server starts, open your browser and go to:

```
http://127.0.0.1:5000
```

---

## 4. How to Run the Tests for the Application

Currently, **manual testing** is supported. Automated tests can be added in the future.

### ✅ Manual Testing Workflow

1. Register a new user at `/register`  
2. Log in via `/login`  
3. Navigate through the following pages and test functionalities:

| Page             | URL               | What to Test                                |
|------------------|-------------------|---------------------------------------------|
| Workout Logging  | `/workout/`       | Add, delete, and share workout records      |
| Shared Workouts  | `/workout/shared` | View workouts shared to you                 |
| Analytics        | `/analytics/`     | View stats: total time, best 5k, etc.       |
| Profile          | `/profile/`       | View user info (username, gender, birthdate) |

4. Test **CSRF Protection**:
   - Check the `X-CSRFToken` header in DevTools → Network  
   - Submit invalid or missing tokens to verify protection

5. Ensure **User Data Isolation**:
   - A user should only see their own data unless it's shared with them