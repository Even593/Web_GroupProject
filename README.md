# FitTrack — Web-based Fitness Tracker

## 1. Purpose and Design

**FitTrack** is a web-based fitness and activity tracking platform that allows users to:
- Record personal workout logs (duration, calories, notes)
- View personal statistics and weekly trends
- Share workout records with specific users (A → B, but not to C)
- Maintain privacy with user-level filtering
- Access a personal profile dashboard

The application is designed using Flask (Python) with Jinja templates and Bootstrap for frontend, SQLAlchemy for database handling, and Chart.js for analytics visualisation.

---

## 2. Group Members

| UWA ID     | Name         | GitHub Username |
|------------|--------------|-----------------|
| 24235608   | XI Qin       | xiqin2049       |
| 24368182   | Junyu Zhang  | fish47          |
| 24094198   | Yifan Lu     | Even593         |
| 23998001   | Leo Yuan     | *(Not linked)*  |

Repository: [https://github.com/Even593/Web_GroupProject](https://github.com/Even593/Web_GroupProject)

---

## 3. How to Run Locally

### Step 1 – Clone the repository

- Open a terminal
- Run `git clone https://github.com/Even593/Web_GroupProject.git`
- Then run `cd Web_GroupProject`

---

### Step 2 – Create and activate a virtual environment

- **macOS/Linux:**
  - Run `python -m venv .venv`
  - Run `source .venv/bin/activate`

- **Windows:**
  - Run `.venv\Scripts\activate`

---

### Step 3 – Install dependencies

- Make sure your virtual environment is activated
- Run `pip install flask flask-sqlalchemy flask-wtf`
- (Optional) If using a `requirements.txt` file, run `pip install -r requirements.txt`

---

### Step 4 – Set environment and launch the app

- **macOS/Linux:**
  - Run `export FLASK_APP=app`
  - Run `export FLASK_ENV=development`
  - Run `flask run`

- **Windows (Command Prompt):**
  - Run `set FLASK_APP=app`
  - Run `set FLASK_ENV=development`
  - Run `flask run`

- Open your browser and go to: `http://127.0.0.1:5000`

---

### Tips

- Ensure all commands are run from the **project root** (`Web_GroupProject/`)
- If `flask` command is not recognized, make sure your environment is activated
- Press `Ctrl + C` to stop the development server

---

