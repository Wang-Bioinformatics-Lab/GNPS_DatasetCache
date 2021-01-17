# main.py
from app import app
from models import *
import views
import create_database

if __name__ == '__main__':
    create_database.create_database()
    app.run(host='0.0.0.0', port=5000)
