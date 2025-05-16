# Script to create all tables in the database using Flask app context
from app import create_app, db

app = create_app()
with app.app_context():
    db.db.create_all()
    print("All tables created.")
