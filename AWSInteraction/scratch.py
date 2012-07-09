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
import SQLite
import shutil
import tarfile
import os
import re
import gzip
import pySolr

class ImportProp:


#    prop_db = None                     #SQLite.SQLite(conf.PROP_DB_PATH)
    solr_db = None
    loc_db = None

    #user provided variables
    date = None
    path = None
    

    found = False

    def __init__(self):
        self.paths = [conf.FSEARCH_LOCAL, conf.FSEARCH_PATH_LIST]
        self.parser = OptionParser(usage="Usage: <pyFetch.py>: [options] arg1 arg2")
        self.parser.add_option("-d", "--date", action="store", type="string", dest="date", help="Add an origin date for file archiving")
        self.parser.add_option("-p", "--path", action="store", type="string", dest="path", help="Add a path to search for files")
        (options, args) = self.parser.parse_args()
        print options.date
        if options.date:
            try:
                valid_date = time.strptime(options.date, '%d/%m/%y')
            except ValueError:
                print "Invalid date entry, exiting"
                exit()

    def check_date(self, prop):
        #If a date existed for this proposal, return it
        str = "select status_date from prop where nsf_id =%s" %prop
        result = self.query_db(str, self.prop_db, conf.PROP_DB_PATH)
        if result[0]:
            return result[0][0]
             
    def update_loc(self, nsf_id, field, text):
        str = 'UPDATE prop SET %s="%s" WHERE nsf_id=%s'%(field,text,nsf_id)
        self.query_db( str, self.loc_db, conf.LOC_DB_PATH)

    def check_prop_loc(self, prop, ftype):
        str = "select * from prop where nsf_id=%s"%prop
        result = self.query_db(str, self.loc_db, conf.LOC_DB_PATH)
        if result[0]:
            if ftype == "PDF":
               #if a pdf hasn't been captured
               if not result[0][H_PDF]:
                   print "add new data"
#            elif ftype == "XML":
#            elif ftype == "NWF":
        else:
            print "No result found"

    def check_prop_update(self, prop, date):
        """ checks to see if prop needs update, true = update
            false = ignore"""
        str = "select status_date from prop where nsf_id=%s"%prop
        result = self.query_db(str, self.loc_db, conf.LOC_DB_PATH)
        if result[0][7]:
            if not result[0][7] == date:
               return False
        return true
        

    def query_db(self, query, dbhandle, dbname):        
        if not dbhandle:
            dbhandle = SQLite.SQLite(dbname)
        result = dbhandle.c.execute(query).fetchall()
        return result

    def __del__(self):
        print "script terminated"
#        self.compress_all_tar("/home/ptr/workgroup/python/fetch/")



#####################old tests#################################################

#####################Solr Tests################################################
    def clear_solr(self, url, port):
        curl = url + ":" + port + "/solr"
        conn = pySolr.Solr(curl)
        print curl
        conn.delete(q="*:*")
        conn.commit()

    def solr_update_xml(self, input):      
        url = "%s%s/%scommit=true%s%s '%s'"%(conf.SOLR_URL, conf.SOLR_PUB_PORT, 
			       conf.SOLR_UPDATE_URL, conf.SOLR_FILE_CONTENT, 
			       conf.SOLR_BINARY_UPLOAD, input)
        conn = pySolr.Solr("http://localhost:9001/solr")
        tmp = []
        tmp.append({"id":"test", "time":"4", "digits":5555, "status":55})
        conn.add(tmp)
        conn.commit()
###############################################################################

#####################Tar Tests#################################################
    def add_to_tar(self, tarf, fname):
        tar_name = tarf + ".tar"
        ctar_name = tarf + ".tar.gz"
        print "tar[%s]ctar[%s]"%(tar_name, ctar_name)
        #if an uncompressed tar file exists, add to it.
        #If no archive exists, create it then add to it.        
        if os.path.isfile(tar_name) or not os.path.isfile(ctar_name):
            try:
                print "adding %s to tar:%s" %(fname, tar_name)
                tar = tarfile.open(tar_name, "a")
                tar.add(fname)
                tar.close()
            except:
                print "Exception found adding tar to uncompressed tar file:", sys.exc_info()[0]
        #check if there is a compressed tar file
        elif os.path.isfile(ctar_name):
            try:
                print "Extracting from ctar:%s" %ctar_name
                tar = tarfile.open(ctar_name, "r:gz")
                tar.extractall()
                tar.close()
                os.remove(ctar_name)
                print "exiting"
                self.add_to_tar(tarf, fname)
            except TypeError as e:
                print "Exception found trying to extract from compressed tar file(%s)" % e
            

    def compress_all_tar(self, path):
#        for path in conf.ARCHIVE_FOLDERS:         
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
