# main.py
import sys
from app import db
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

    # Try to run the migrations
    try:
        sys.path.insert(0, "migrations")
        import migrate_11_12_2024

        migrate_11_12_2024._migrate(db)
        print("MIGRATION SUCCEEDED")
    except:
        print("MIGRATION FAILED")
        pass
