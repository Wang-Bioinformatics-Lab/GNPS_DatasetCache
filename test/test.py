import sys
sys.path.insert(0, "..")
import compute_tasks

def test():
    import requests
    import requests_cache
    requests_cache.install_cache('demo_cache')

    from models import Filename
    Filename.create_table(True)

    # Query 
    print(Filename.select().count())


    filename_db = Filename(filepath="XZ", dataset="X", collection="X")
    save_key = filename_db.save()
    print(save_key)

    print(Filename.select().count())

    #compute_tasks.populate_ftp()

