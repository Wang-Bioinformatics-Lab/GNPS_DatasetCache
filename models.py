# models.py

from peewee import *
from app import db

class Filename(Model):
    filepath = TextField(primary_key=True)
    dataset = TextField()
    collection = TextField()

    class Meta:
        database = db
