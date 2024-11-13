from playhouse.migrate import *
from peewee import SqliteDatabase

def _migrate(db):
    # SQLite example:
    #db = SqliteDatabase("./database/database.db", pragmas=[('journal_mode', 'wal')]) #Production
    migrator = SqliteMigrator(db)

    # Define the new fields
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

    # Perform the migration
    with db.atomic():
        migrate(
            migrator.add_column('uniquemri', 'RT_Range_in_Min', RT_Range_in_Min),
            migrator.add_column('uniquemri', 'Top_CEs', Top_CEs),
            migrator.add_column('uniquemri', 'Top_CE_Counts', Top_CE_Counts),
            migrator.add_column('uniquemri', 'MassAnalyzer', MassAnalyzer),
            migrator.add_column('uniquemri', 'Ionization', Ionization),
            migrator.add_column('uniquemri', 'top_k_prec_mz_diffs', top_k_prec_mz_diffs),
            migrator.add_column('uniquemri', 'top_k_prec_mz_diff_counts', top_k_prec_mz_diff_counts),
            migrator.add_column('uniquemri', 'conseq_ms2_prec_increase', conseq_ms2_prec_increase),
            migrator.add_column('uniquemri', 'conseq_ms2_prec_decrease', conseq_ms2_prec_decrease),
            migrator.add_column('uniquemri', 'conseq_ms2_prec_equal', conseq_ms2_prec_equal),
            migrator.add_column('uniquemri', 'prec_prop_equal', prec_prop_equal),
            migrator.add_column('uniquemri', 'prec_prop_increase', prec_prop_increase),
            migrator.add_column('uniquemri', 'prec_prop_decrease', prec_prop_decrease),
            migrator.add_column('uniquemri', 'classification', classification),
        )