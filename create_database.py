# main.py
from app import app
from models import *

def create_database():
    Filename.create_table(True)

if __name__ == '__main__':
    create_database()
