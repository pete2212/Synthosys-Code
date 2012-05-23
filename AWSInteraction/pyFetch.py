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

""" functional diagram
   
    Import_data:
    existing data:
        from database?
            Verify_db;
            Open db;
            test with sample query and verify results
            select fyear from prop;
            sort list from high to low
            for each year from start to finish  query all files:            
               month = 1
               while month < 13:                  
                  select dd_month, fpropid, status from prop where month = init and fyear == year;)
                  loc= locate_file( fpropid)
                  if loc != False:
                       add_id(propid, loc)
            if month < 12
                month += 1
            else 
                year += 1
                month = 1


"""

import sys
import pyFetchConf
sys.path.append(pyFetchConf.CODE_PATH)
sys.path.append("/home/ptr/workgroup/python/modification_scripts")
from xml_parser import XML_Interaction
import SQLite
import shutil
import pycurl
import os

class ImportProp:

    
    prop_db = SQLite.SQLite(pyFetchConf.PROP_DB_PATH)
    solr_db = None
    loc_db = None
    found = False

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
#prop_db = SQLite.SQLite(pyFetchConf.PROP_DB_PATH)
        else:
            print "Invalid source"
            exit()

    def query_by_year(self):
        """queries prop_db from YSTART to YEND, calls indexing functions
           for old data
  
        Args:
           None
 
        Returns:
           None

        Raises:
           None 
        """
        dec_found = 0
        dec_missing = 0
        award_found = 0
        award_missing = 0
        proposal_found = 0
        proposal_missing = 0

        year = pyFetchConf.YEND
        #TODO understand Ron's API better
        while year >= pyFetchConf.YSTART:
            for month in range(0,13):
#                print "q:select dd_date, nsf_id, status from prop where dd_date like %s/%02d/%% order by dd_date DESC" %(year, month)
                query = ('select dd_date, nsf_id, status from prop where dd_date like "%s/%02d/%%" order by dd_date DESC' % (year, month) )
                result = self.prop_db.c.execute(query).fetchall()
#                result2 = self.prop_db.fetch( table="prop", field=[ "dd_date", "nsf_id", "status", "abstract"], limit="dd_date like 11/02/%%" )
#            result2 = self.prop_db.fetch( "prop", "fyear" 
                import time
                count = 0;
                for entry in result:
#                    print "%s,%s,%s" % (entry[0], entry[1], entry[2])
                    result = self.get_prop(entry[1])
                    if entry[2] == "decline":
                        if result[0]:
                            dec_found += 1
                        else:
                            dec_missing += 1
                    if entry[2] == "award":
                        if result[0]:
                            award_found += 1
                        else:
                            award_missing += 1
                    if entry[2] == "propose":
                        if result[0]:
                            proposal_found += 1
                        else:
                            proposal_missing +=1            
                    if result[0]:
                       self.move_data(entry, found)
#                    time.sleep(1)
#                self.move(entry)
#                self.add_solr(entry)
            year -= 1
        print "Document Status report:"
        print "decline_f[%s] decline_m[%s] award_f[%s] award_m[%s] prop_f[%s] prop_m[%s]" % (dec_found, dec_missing, award_found, award_missing, proposal_found, proposal_missing)
   
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
           self.solr_db = SQLite.SQLite(pyFetchConf.SOLR_DB_PATH)
        #solr_db.addSQL(entry, table="prop")
        print "Insert into vals into db[%s,%s,%s,%s,%s]"%(entry[0],entry[1],entry[2],entry[3],entry[4])
        self.solr_db.c.execute("insert into prop values (?,?,?,?,?)", entry)
        self.solr_db.commit() 

    def add_solr(self, entry):
        """Adds data to private or public and private database and mark location in DB
        
        Args:
            entry: list of fields to add to solr database
  
        Returns:
            None
  
        Raises:
            None
        """
        if solr_db == "": 
            solr_db = SQLite.SQLite(pyFetchConf.SOLR_DB_PATH)
        if entry.status:
            port = pyFetchConf.PRPORT
            type = "private"
        else:
            port = pyFetchConf.PRPORT

        self.add_solr_db(entry) #push the current data to sql db for backup

        #TODO This will upload to solr database, but not cause a commit, test whether commit
        #be per item or total
        url = "%s%s/solr/%s%s%s%s" %(pyFetchConf.SOLR_URL, port,
        pyFetchConf.SOLR_UPDATE_URL, pyFetchConf.SOLR_BINARY_UPLOAD,
	fpath, SOLR_FILE_CONTENT)

#pyFetchConf.SOLR_URL + port + "/solr" + pyFetchConf.SOLR_UPDATE_URL +
#        pyFetchConf.SOLR_BINARY_UPLOAD + fpath + SOLR_FILE_CONTENT

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buf.write())
        c.perform()
    
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

    def move_data(self, entry, flocation):
        """ To move data to new location and mark location in DB
 
        Args:
            entry: list of fields to add to solr database
            loc: original file path

        Returns:
            None
     
        Raises:
            None
        """
        if loc_db == None:
            loc_db = SQLite.SQLite(pyFetchConf.LOC_DB_PATH)

        date = entry.dd_date.split('/')
        month = date[0]
        year = date[2]

        #TODO define PDF/XML/XMLWELLFORMED
        #PDF
        if entry[1]:
            newfile = pyFetchConf.OPATH + "/pdf/" + entry.nsf_id
            if os.path.isfile(entry[2]):
                if not os.path.isfile(newfile):
                    shutil.copy2(entry[2], newfile)
                else:
                    print "File already exists %s" % newfile
            else:
                print "File % not found" % entry.nsf_id

       
    def get_prop(self, fname):
        #Located/pdf located/xml located/well formed located
        found = [False, False, False, False]
        """searches through default paths for file
 
        Args: 
            fname = nsf id to search for within filenames

        Returns:
            None
 
        Raises:
            None
        """
        #Located/pdf located/xml located/well formed located
        found = [False, False, False, False]

        found = self.locate_prop(fname, pyFetchConf.FSEARCH_PATH_LIST) #search Dave's directory first
        if not found:
            for x in os.listdir( pyFetchConf.FSEARCH_LOCAL ):
                file = pyFetchConf.FSEARCH_LOCAL + x
                if os.path.isfile(file):
                    if not file.find(fname) == -1:
                        print "%s found at loc $s" %(fname, file)
                        found[0] = True
                        if file[-3:] == "pdf":
                            found[1] = True
                            found[2] = file
                        elif file[-3:] == "xml":
                            found[3] = True
                            found[4] = file
                        elif file[-3:] == "NWF":
                            found[5] = True
                            found[6] = file
                        else:
                            print "File found but unknown extension %s" % file
        #if data is found, push to database and move file for archiving
        result = found[0]

        return found
        
    def locate_prop(self, fname, root=pyFetchConf.FSEARCH_PATH_LIST):
        """Search directory tree for file
               Args:
                   fname: file name to search for
                   root: starting path to search

               Returns:
                   List of file extensions found (pdf, xml, xmlwellformed)
        """
        #pdf/xml/xmlwellformed
        found = [False, False, "", False, "", False, ""]
#        print 'searching for %s'%fname
        for x in os.listdir(root):
            file = root + x
            if os.path.isfile(file):
                if not file.find(fname) == -1:
                    print "%s found at loc %s"%(fname, file)                  
                    found[0] = True
                    if file[-3:] == "pdf":
                        found[1] = True
                        found[2] = file
                    elif file[-3:] == "xml":
                        found[3] = True
                        found[4] = file
                    elif file[-3:] == "NWF":
                        found[5] = True
                        found[6] = file
                    else:
                        print "File found but unknown extension %s" % file                    
                    
            else:
                if x == "txt" or x == "txt_update":
                    return
                file += "/"
                self.locate_prop(fname, file)
        return found 

#        dir_list = os.listdir(root)
#        for fname in dir_list:
        
#       tar = tarfile.open(pyFetchConf.ORIGINAL_LOC)
#       for item in tar.getmembers():
#           if not item.find( fname ) == -1:
#               f=tar.extractfile(item)
#               f.write(pyFetchConf.OPATH + fname )
      
i = ImportProp()
i.import_data()
i.query_by_year()
#nsf_id/dd_date/summary/description
#entry = ["11/10/1981", "11527", "Status field", "summary field", "description field"]
#entry = ["11111", "11/10/1981", "summary", "description", "status"]
#i.add_solr_db( entry )
#i.format_xml(entry)
