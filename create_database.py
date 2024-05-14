# main.py
from app import app
from models import *

def create_database():
    try:
        Filename.create_table(True)
    except:
        pass

    try:
        UniqueMRI.create_table(True)
    except:
        pass

if __name__ == '__main__':
    create_database()
