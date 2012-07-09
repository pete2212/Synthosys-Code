#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#
#  Copyright 2012 Clean ubuntu 11.10 <ptr@ubuntu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import sys
import pyFetchConf as conf
sys.path.append(conf.CODE_PATH)
sys.path.append("/home/ptr/workgroup/python/modification_scripts")
from xml_parser import XML_Interaction
from optparse import OptionParser
from datetime import datetime
import xml_conf as xml
import SQLite
import shutil
import tarfile
import pySolr
import gzip
import os
import re

class ImportProp:

    #class variables defined as database handles    
    prop_db = None                     #SQLite.SQLite(conf.PROP_DB_PATH)
    solr_db = None
    loc_db = None

    #user provided variables
    data = None
    path = None

    found = False
##################################Constructor and Destructor###################
    def __init__(self):
        """ Constructor for Import class, sets default paths and parses command
            line
       
            Args:
                None

            Returns:
                None
            Raises:
                ValueError if improper date is entered as argument
        
        """
        #set up paths to search
        self.paths = [conf.FSEARCH_LOCAL, conf.FSEARCH_PATH_LIST]

        #setup command line parsing library and search for input
        self.parser = OptionParser(
            usage="Usage: <pyFetch.py>: [options] arg1 arg2")
        self.parser.add_option("-d", "--date", action="store",
            type="string", dest="date", help="Add an origin date for file archiving")
        self.parser.add_option("-p", "--path", action="store", type="string", 
            dest="path", help="Add a path to search for files")
        (options, args) = self.parser.parse_args()

        #Verify if date has been provided and it's valid
        if options.date:
            try:
                valid_date = datetime.strptime(options.date, "%m/%d/%Y")
                self.date = options.date
            except ValueError:
                print "Invalid date entry, exiting"
                exit()
        else:
            loc_date = datetime.now()
            self.date = loc_date.strftime("%m/%d/%Y")

        #Add additional path information to global prop search list
        if options.path:
            self.paths.append(options.path)

    def __del__(self):
        """Destructor, goes through all defined paths and attempts to remove
           old compressed tar files and compress their replacements
  
           Args: 
	       None
     
           Returns:
               None

           Raises:
               None	       
        """
        self.compress_all_tar()		       
        print "terminated"
###############################################################################

    def import_data(self, source="db"):
        """allows importing of data by month based on NSF ID, date, and status
            
            Args:
                source: source of data input.  Default is db for database
        
            Returns:
                None
        
            Raises:
                None
        """
        if source == "db":
           print "using proposal.s3 db as source"
           self.query_by_year()
        else:
            print "Invalid source"
            exit()

    def import_data_from_folder(self, fname):
        """Grabs proposal data from xml/pdf/nwf files in given folder
  
        Args:
           fname: Name of folder

        Returns:
           None

        Raises:
           None
        """
        found = [False, False, "", False, "", False, ""]
        for fpath in paths:
            self.locate_prop(fname, found, fpath)

    def query_by_year(self, ystart=conf.YSTART, yend=conf.YEND):
        """queries prop_db from YSTART to YEND, calls indexing functions
           for old data
  
        Args:
           None
        
        Returns:
           None
        
        Raises:
           None 
        """

        if not self.prop_db:
            self.prop_db.open(conf.PROP_DB_PATH)
        fmissing = open("missing_props.txt", 'a+')

        dec_found = 0
        dec_missing = 0
        award_found = 0
        award_missing = 0
        proposal_found = 0
        proposal_missing = 0
        fetch_result = [False, False, "", False, "", False, ""] 
        year = conf.YEND
        #TODO understand Ron's API better
        while year >= conf.YSTART:
            for month in range(0,13):
                query = ('select dd_date, nsf_id, status from prop where dd_date like "%s/%02d/%%" order by dd_date DESC' % (year, month) )
                result = self.prop_db.c.execute(query).fetchall()               
                for entry in result:
#                    print "%s,%s,%s" % (entry[0], entry[1], entry[2])
                    fetch_result = self.get_prop(entry[1])
                    if fetch_result[0]:
                        print fetch_result
#                        self.move_found_data(entry, fetch_result)
                    else:
                        #print value of missing prop
                        missing = entry[1] + ', '
                        fmissing.write(missing)
#                self.add_solr(entry)
            year -= 1
   
    def add_loc_db(self, entry):
        """Adds data into local sql database to record archived file location

           Args:
               Entry list which includes data to be added in format:
               nsf_id, int, primary key/has_pdf, int(bool)/pdf_loc, string/
               has_xml,int(bool)/xml_loc, string/has_nwf, int(bool)/
               nwf_loc(string)

 
           Returns:
               True if successful, False if error

           Raises:
               None
        """
            
        if not self.loc_db:
            self.loc_db.open(conf.LOC_DB_PATH)
        try:           
            self.loc_db.c.execute("insert into prop values (?,?,?,?,?,?,?)", entry)
            self.loc_db.commit()
        except IndexError:
            print "Index error for id %s, most likely non-unique ID" % entry[0]
        except:
            print "Error for id %s: %s" %( entry[0], sys.exc_info()[0])

        
    def add_solr_db(self, entry):
        """Adds data into local sql database for easy recall/reload of solr
    
           Args:
               entry: data to be entered in format:
                      nsf_id/dd_date/summary/description
          
           Returns:
               None
 
           Raises:
               None
        """

        if not self.solr_db:
            self.solr_db = SQLite.SQLite(conf.SOLR_DB_PATH)
        #solr_db.addSQL(entry, table="prop")
        try:
            print "Insert vals into db[%s,%s,%s,%s,%s]"%(entry[0],entry[1],entry[2],entry[3],entry[4])
            self.solr_db.c.execute("insert into prop values (?,?,?,?,?)", entry)
            self.solr_db.commit() 
        except:
            print "Error:", sys.exc_info()[0]
 
    def remove_id_solr_db(self, value):
        """Remove entry from solr database

           Args:
               entry: data entry to be removed from db
        """
        if not self.solr_db:
            self.solr_db = SQLite.SQLite(conf.SOLR_DB_PATH)
              
        query = "delete from prop where nsf_id = %s" % value
             
        self.solr_db.c.execute(query)

    def add_solr_entry(self, entry, entry_type):
        """Adds data to private or public and private database and mark location in DB
        
        Args:
            entry: list of fields to add to solr database
  
        Returns:
            None
  
        Raises:
            None
        """
        if not self.solr_db: 
            self.solr_db = SQLite.SQLite(conf.SOLR_DB_PATH)
             
        if entry[4]:
            port = conf.SOLR_PRI_PORT
            type = "private"
        else:
            port = conf.SOLR_PUB_PORT
            
        if entry_type == "memory":
           self.xml_str = self.format_xml(entry)
        else:
           self.xml_str = self.get_xml_file(entry)

        self.add_solr_db(entry) #push the current data to sql db for backup

        #TODO This will upload to solr database, but not cause a commit, test whether commit
        #be per item or total
    

    def format_xml(self, entry, format="solr", status="private"):
        """Format incoming information into xml based on format type
          
        Args:
            format: the format type for data response, default is solr
            entry: Data to be formatted
 
        Returns:
            String of xml data in requested format

        Raises:
            None         
        """
#        import xml_parser
        if format == "solr":            
            x = XML_Interaction()
            result = x.create_solr_doc(entry, status)
            print "new xml data:\n%s" % result
       
    def move_found_data(self, id, type, flocation, p_date):
        """ To move data to new location and mark location in DB 
            and archive/backup data
 
        Args:
            entry: list of fields to add to solr database
            loc: original file path

        Returns:
            None
     
        Raises:
            None
        """
        if self.loc_db == None:
            self.loc_db = SQLite.SQLite(conf.LOC_DB_PATH)

        tar = ""
        date = p_date.split('/')
        month = date[1]
        year = date[0]
        
        if type == "pdf":
            newfile = conf.PDF_ARCHIVE + entry[conf.NSF_ID] + ".pdf"
            if os.path.isfile(flocation) and flocation[-3:] == "pdf":
                if not os.path.isfile(newfile):
                    shutil.copy2(flocation, newfile)
                    tar = conf.PDF_ARCHIVE + "pdf_" + month + "_" + year + ".tar"
#                        print "creating tar %s" % tar
                    self.add_to_tar(newfile, tar)
                else:
                    print "PDF file already exists %s" % newfile
            else:
                print "PDF file %s not found" % flocation

        if type == "xml":
            newfile = conf.XML_ARCHIVE + entry[conf.NSF_ID] + ".xml"
            if os.path.isfile(flocation) and flocation[-3:] == "xml":
                if not os.path.isfile(newfile):
                    shutil.copy2(flocation, newfile)
                    tar = conf.XML_ARCHIVE + "xml_" + month + "_" + year + ".tar.gz"
                    self.add_to_tar(newfile, tar)
                else:
                    print "xml file already exists %s" % newfile
            else:
                print "XML file %s not found" % flocation

        if type == "nwf":
            newfile = conf.NWF_ARCHIVE + entry[conf.NSF_ID] + ".nwf"
            if os.path.isfile(flocation) and flocation[-3:] == "nwf":
                if not os.path.isfile(newfile):
                    shutil.copy2(flocation, newfile)
                    tar = conf.NWF_ARCHIVE + "nwf_" + month + "_" + year + ".tar.gz"
                    self.add_to_tar(newfile, tar)
                else:
                    print "NWF file already exists %s" % newfile
            else:
                print "NWF file %s not found " % flocation
        #update database with tar location 
        self.update_loc(id, type, tar, date)

    def get_prop(self, fname):
        #Located/pdf located/xml located/well formed located
        found = [False, False, "", False, "", False, ""]
        """searches through default paths for file
 
        Args: 
            fname = nsf id to search for within filenames

        Returns:
            None
 
        Raises:
            None
        """
        #Located/pdf located/xml located/well formed located

        found = self.locate_prop(fname, found, conf.FSEARCH_PATH_LIST) #search Dave's directory first
        #search local data directory for other file formats
#        if not found[0] or ( (not found[1]) or (not found[3]) or (not found[5]) ):
        for x in os.listdir( conf.FSEARCH_LOCAL ):
            file = conf.FSEARCH_LOCAL + x
            if os.path.isfile(file):
                if not file.find(fname) == -1:
#                    print "get prop %s found at loc $s" %(str(fname), str(file))
                    found[0] = True
                    if file[-3:] == "pdf":
                        found[1] = True
                        found[2] = file
                    elif file[-3:] == "xml":
                        found[3] = True
                        found[4] = file
                    elif file[-3:] == "nwf":
                        found[5] = True
                        found[6] = file
                    else:
                        print "File found but unknown extension %s" % file
#                    print "ext %s found, structure: %s" %(file[-3:], found)
        #if data is found, push to database and move file for archiving
#        print "found val to return %s" % found
        return found
        
    def locate_prop(self, fname, found, root=conf.FSEARCH_PATH_LIST):
        """Search directory tree for file
               Args:
                   fname: file name to search for
                   root: starting path to search

               Returns:
                   List of file extensions found (pdf, xml, xmlwellformed)
        """
        #pdf/xml/xmlwellformed
#        found = [False, False, "", False, "", False, ""]
#        print 'searching for %s'%fname
        for x in os.listdir(root):
            file = root + x
            if os.path.isfile(file):
                if not file.find(fname) == -1:
#                    print "locate_prop:%s found at loc %s, ext.:%s"%(fname, file, file[-3:])                  
                    found[0] = True
                    if file[-3:] == "pdf" and not found[1]:
                        found[1] = True
                        found[2] = file
#                       print found
                    elif file[-3:] == "xml" and not found[3]:
                        found[3] = True
                        found[4] = file
#                        print found
                    elif file[-3:] == "NWF" and not found[5]:
                        found[5] = True
                        found[6] = file
#                        print found
                    else:
                        print "File found but unknown extension %s" % file                 
                if found[1] and found[3] and found[5]:
                    print "all docs found for %s" % fname
                    return found
            else:
                if x == "txt" or x == "txt_update":
                    return found
                file += "/"
                self.locate_prop(fname, found, file)
        return found 

    def injest_prop_by_folder(self, path):
        """
        """
        update_field = 0
        field_text = 0
        text = ""
        valid = True

        for x in os.listdir(path):
            file = path + "/"+ x
            if os.path.isfile(file):
                #locate the ID within the file
                id = re.search('[0-9]{7}', file)
                id_str = id.group()
                print id_str
                if id_str.isdigit():
                    valid = True
                    #verify id
                    date = self.check_date(id_str)
                    #If date does not yet exist in system, set date to global
                    if not date:
                        date = self.date
                    split = date.split('/')
                    month = date[1]
                    year = date[0]        
                    print "month[%s]year[%s]"%(month,year) 
                    if file[-3:] == "pdf":
                        update_field = conf.PDF_FOUND
                        field_text = conf.PDF_LOC
                        text = file
                    elif file[-3:] == "xml":
                        update_field = conf.XML_FOUND
                        field_test = conf.XML_LOC
                        text = file
                        self.update_solr(id_str, file)
                    elif file[-3:] == "nwf":
                        update_field = conf.NWF_FOUND
                        field_test = conf.NWF_LOC
                        text = file
                    else:
                        valid = False
                    if valid:
#                        self.update_loc(id_str, update_field, text, date)
                        self.move_found_data(id_str, update_field, text, date)

##########################DB Manipulation######################################
    def check_date(self, nsf_id):
        """ Verify if any previuos data information exists for prop
        """
        str = "select status_date from prop where nsf_id=%s"%nsf_id
        result = self.query_db(str, self.loc_db, conf.LOC_DB_PATH)
        if result:
            return result[0][0]
        #fallback to prop db for date
        result = self.query_db(str, self.prop_db, conf.PROP_DB_PATH)
        if result:
            return result[0][0]
        return False

    def check_solr_entry(self, nsf_id):
        """ Queries solr db to verify entry exists 
        """
        str = "select * from prop where nsf_id = %s"%nsf_id
        result = self.query_db(str, self.solr_db, conf.SOLR_DB_PATH)
        return result
    
    def verify_loc_data(self, nsf_id):
        """Verifies the data exists
        """
        str = "select * from prop where nsf_id = %s"%nsf_id
        result = self.query_db(str, self.loc_db, conf.LOC_DB_PATH)

    def add_dict_to_solr_db(self, nsf_id, data):
        check_id = self.check_solr_entry(nsf_id)
        print data
        if not check_id:
            input = [ data["id"],data["date"],data[xml.SUM_TAG],data[xml.DESC_TAG], 
                    data["Proposal_Status"] ]
        
            self.add_to_db(input, self.solr_db, conf.SOLR_DB_PATH)
        else:
            print "entry already exists in db"

    def update_loc(self, nsf_id, field, text, date):
        """ Creates a string to update a specific field within location db
        """
        valid_entry = self.verify_loc_data(nsf_id)
        if valid_entry:
            str = ('UPDATE prop SET %s="%s, %s=%s" WHERE nsf_id=%s'%
                   ((field-1), 'True',field,text,nsf_id))
            self.modify_db(str, self.loc_db, conf.LOC_DB_PATH)
        else:
            data = [nsf_id, "False", "", "False", "", "False", "", self.date]
            data[field-1] = True
            data[field]=text
            self.add_to_db(data, self.loc_db, conf.LOC_DB_PATH) 

    def query_db(self, query, dbhandle, dbname):
        """ Queries given db for a given instruction
        """
        if not dbhandle:
            dbhandle = SQLite.SQLite(dbname)
        print query
        result = dbhandle.c.execute(query).fetchall()
        return result

    def modify_db(self, query, dbhandle, dbname):
        """ Quries given db with given instruction, commits result
        """
        if not dbhandle:
            dbhandle = SQLite.SQLite(dbname)
            dbhandle.c.execute(query)
            dbhandle.commit()

    def add_to_db(self, data, dbhandle, dbname):
        """ Adds a new entry to given database
        """
        if not dbhandle:
            dbhandle = SQLite.SQLite(dbname)
        #interate over number of data elements to build insert cmd
        entries = len(data) 
        qstr = "insert into prop values ("
        qstr += (", ".join(["?"] * entries))
        qstr += ")"
        print qstr
#        for index in entries:             
#            qstr = qstr + "?,"
#        qstr = qstr + "?"
        dbhandle.c.execute(qstr, data)
        dbhandle.commit()


###############################################################################

##########################File Manipulation and archiving######################

    def add_to_tar(self, tarf, fname):
        """Checks to see if tar file exists, otherwise looks for compressed file
           with same name and extracts tar file.  Opens or creates tar file and 
           adds to it
        
           Args:
               tarf: tar file name to add to
               fname: file name to be added to tar

           Returns:
               None

           Raises:
               TypeError: Checks to verify all tar operations were successful
        """

        tar_name = tarf + ".tar"
        ctar_name = tarf + ".tar.gz"
        print "tar[%s]ctar[%s]"%(tar_name, ctar_name)
        #if an uncompressed tar file exists, add to it.
        #If no archive exists, create it then add to it.
        if os.path.isfile(tar_name) or not os.path.isfile(ctar_name):
            try:
                tar = tarfile.open(tar_name, "a")
                tar.add(fname)
                tar.close()
            except:
                print "Exception found adding tar to uncompressed tar file:", sys.exc_info()[0]
        #check if there is a compressed tar file
        elif os.path.isfile(ctar_name):
            try:
                tar = tarfile.open(ctar_name, "r:gz")
                tar.extractall()
                tar.close()
                os.remove(ctar_name)
                print "exiting"
                self.add_to_tar(tarf, fname)
            except TypeError as e:
                print "Exception found trying to extract from compressed tar file(%s)" % e

    def compress_all_tar(self, path=None):
        """ Attempts to locate any uncompressed tar folders (.tar extension) 
            and compress them into gzipped tar files (.tar.gz extension)

            Args:
                path: A configurable path to search for files to compress
            Returns:
                None
            Raises: 
                None
        """
        paths = conf.ARCHIVE_FOLDERS
        if path:
           paths.append(path)

        for p in paths:
            for x in os.listdir(path):
                file = x #path + x
                #if an uncompressed file exists
                if os.path.isfile(file) and file[-3:] == "tar":
                    print "Compressing %s" % file
                    #verify if compressed version exists
                    cname = file[:-3] + "tar.gz"
                    print cname
                    tar = tarfile.open(cname, "w:gz")
                    tar.add(file)
                    tar.close()
                    os.remove(file)
###############################################################################

########################################SOLR manipulation section##############
    def update_solr(self, id, file, s_date=None):
        if not s_date:
            s_date = self.date
        solr_dct = {"date": s_date, "id":id}
        print id
        result = self.check_solr_entry(id)
        #if no result returned
        if not result:
            if os.path.isfile(file):
                print file
                x = XML_Interaction()
                result =  x.create_solr_dict(file, solr_dct) 
                self.add_to_solr_dict(result)
                self.add_dict_to_solr_db(id, result)
            else:
                print "Error, non-valid file provided %s" % file
        else:
            print "found"

    def add_to_solr_dict(self, entry, privacy="private"):
        if privacy == "private":
            port = conf.SOLR_PRI_PORT
        else:
            port = conf.SOLR_PUB_PORT
        url = conf.SOLR_URL + ":%s/solr" % port
        print url
        tmp = []
        tmp.append(entry)
        conn = pySolr.Solr(url)
        conn.add(tmp)
        conn.commit()
    
    def clear_solr(self, url, item="*:*", port=conf.SOLR_PUB_PORT):
        """Clears defined item out of solr database, if no item is supplied
           the entire database will be cleared

           Args:
               url: The URL marks the url for the solr server in question
               item: The item you wish to remove from the solr db, ex. id=xxxxx
               port: port solr server is hosted on
 
           Returns:
               None

           Raises:
               None

           
        """
        curl = url + ":" + port + "/solr"
        conn = pySolr.Solr(curl)
        conn.delete(q=item)
        conn.commit()

    
############################################################################
