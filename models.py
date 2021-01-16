# models.py

from peewee import *
from app import db

class Filename(Model):
    filepath = TextField(primary_key=True, index=True)
    dataset = TextField(index=True)
    collection = TextField(index=True)
    is_update = IntegerField() # This tells us if its an update, 0 for not, 1 for update
    update_name = TextField(index=True) # This tells us the update specifics
    create_time = DateTimeField()
    size = IntegerField()
    spectra_ms1 = IntegerField(default=0)
    spectra_ms2 = IntegerField(default=0)

    class Meta:
        database = db
