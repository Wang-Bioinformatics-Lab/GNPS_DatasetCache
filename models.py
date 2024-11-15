# models.py

from peewee import *
from app import db

class Filename(Model):
    usi = TextField(primary_key=True, index=True)

    filepath = TextField(index=True)
    dataset = TextField(index=True)
    collection = TextField(index=True)

    is_update = IntegerField() # This tells us if its an update, 0 for not, 1 for update
    update_name = TextField(index=True) # This tells us the update specifics
    create_time = DateTimeField()
    size = IntegerField()
    size_mb = IntegerField()

    # Types of Data
    sample_type = TextField(index=True) # Default, or GNPS, MTBLS, MWB

    # Mass spec specific information about the files
    spectra_ms1 = IntegerField(default=0)
    spectra_ms2 = IntegerField(default=0)
    instrument_vendor = TextField(index=True, default="")
    instrument_model = TextField(index=True, default="")

    # Administrative
    file_processed = TextField(default="No")

    class Meta:
        database = db

class UniqueMRI(Model):
    usi = TextField(primary_key=True, index=True)

    filepath = TextField(index=True)
    dataset = TextField(index=True)
    collection = TextField(index=True)

    is_update = IntegerField() # This tells us if its an update, 0 for not, 1 for update
    update_name = TextField(index=True) # This tells us the update specifics
    create_time = DateTimeField()
    size = IntegerField()
    size_mb = IntegerField()

    # Types of Data
    sample_type = TextField(index=True) # Default, or GNPS, MTBLS, MWB

    # Mass spec specific information about the files
    spectra_ms1 = IntegerField(default=0)
    spectra_ms2 = IntegerField(default=0)
    instrument_vendor = TextField(index=True, default="")
    instrument_model = TextField(index=True, default="")

    # Detailed Information About the File
    RT_Range_in_Min = FloatField(default=0)
    Top_CEs = TextField(default="")
    Top_CE_Counts = TextField(default="")
    MassAnalyzer = TextField(default="")
    Ionization = TextField(default="")
    top_k_prec_mz_diffs = TextField(default="")
    top_k_prec_mz_diff_counts = TextField(default="")
    conseq_ms2_prec_increase = IntegerField(default=0)
    conseq_ms2_prec_decrease = IntegerField(default=0)
    conseq_ms2_prec_equal = IntegerField(default=0)
    prec_prop_equal = FloatField(default=0)
    prec_prop_increase = FloatField(default=0)
    prec_prop_decrease = FloatField(default=0)

    classification = TextField(default="Unclassified")

    # Administrative
    file_processed = TextField(default="No")

    


    class Meta:
        database = db
