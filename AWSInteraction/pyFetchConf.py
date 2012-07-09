#PATH related information
CODE_PATH = "/home/ron/Govt-API/PythonBase/" #path for code base
ORIGINAL_FILE = "/home/ron/Govt-API/data" #original data
PROP_DB_PATH = "/home/ron/Govt-API/sqlite/proposal.s3" #prop db
SOLR_DB_PATH = "/home/ptr/workgroup/database/solrdata.s3" #path for solr database backup information
LOC_DB_PATH = "/home/ptr/workgroup/database/locdata.s3" #path for newly relocated file data
OPATH = "/home/ptr/docfiles"
FSEARCH_PATH_LIST = "/home/dnewman/update/"
FSEARCH_LOCAL = "/home/ptr/data/2012-05-15/"
PDF_ARCHIVE = "/home/ptr/data/pdf_archive/"
NWF_ARCHIVE = "/home/ptr/data/nwf_archive/"
XML_ARCHIVE = "/home/ptr/data/xml_archive/"
ARCHIVE_FOLDERS = [PDF_ARCHIVE, NWF_ARCHIVE, XML_ARCHIVE]

#URL building
SOLR_URL = "http://localhost"
SOLR_UPDATE_URL = "solr/update?"
SOLR_BINARY_UPLOAD = " --data-binary"
SOLR_FILE_CONTENT = ' -H "Content-type: text/xml"'

#prop related defines 
YSTART = 2004 #start of proposal date range
YEND = 2012 #end of proposal date range

#File extension search results
DOC_FOUND = 0
PDF_FOUND = 1
PDF_LOC = 2
XML_FOUND = 3
XML_LOC = 4
NWF_FOUND = 5
NWF_LOC = 6

#File Extension db layout
L_NSF_ID = 0
H_PDF = 1
L_PDF = 2
H_XML = 3
L_XML = 4
H_NWF = 5
L_NWF = 6
L_DATE = 7

#Location DB layout (mapped above)
loc = { 0:"nsf_id", 1:"has_pdf", 2:"pdf_loc", 3:"has_xml", 4:"xml_loc", 5:"has_nwf",
    6:"nwf_loc", 7:"ss_date"}

#SOLR related defines
SOLR_PRI_PORT = 9000 #internal port for solr public instance
SOLR_PUB_PORT = 9001 #internal port for solr private instance

#SQL result defines
NSF_ID = 1
DD_DATE = 0
status = 2

#HELP strings
FETCH_USAGE = "USAGE: Please specify source of data to fetch:\n\t-a from archive\n\t-f {file name} from file"
