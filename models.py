# models.py

from peewee import *
from app import db

class Filename(Model):
    filepath = TextField(primary_key=True, index=True)
    dataset = TextField(index=True)
    collection = TextField(index=True)

    class Meta:
        database = db
