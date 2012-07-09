import sys
import pyFetchConf as conf
from pyFetch import ImportProp 


i = ImportProp()

#i.update_solr(1241764, "/home/ptr/data/2012-05-15/1241764RC.xml")
i.injest_prop_by_folder("/home/ptr/data/test_dir")

#def ingest_archive(overwrite=False, location=conf.PROP_DB_PATH):
#    i.import_data()    

#def ingest_folder(type, name, overwrite=False):
#    pass
"""
if len(sys.argv) > 1:
    source = "archive"
    file = ""
    if sys.argv[1] == "-a":
        source = "archive"
        print sys.argv
        if len(sys.argv) < 3:
            ingest_archive( )
        else:
            ingest_archive( location = sys.argv[2])
    elif sys.argv[1] == "-f":
        source = "file"
        if len(sys.argv) > 2:
            file = sys.argv[2]
            ingest_folder("file", file )
        else:
            print ("Error, no filename\n%s" % (conf.FETCH_USAGE))
    elif sys.argv[1] == "-folder":
        i.injest_prop_by_folder(conf.FSEARCH_LOCAL)
    else:
        print conf.FETCH_USAGE
else:
    print conf.FETCH_USAGE
"""

