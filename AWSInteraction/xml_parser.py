#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  xml_parser.py
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
#  
from xml.dom.minidom import parse
#import xml.etree.ElementTree as xml
from elementtree.ElementTree import ElementTree, Element, SubElement, dump
import sys
import os
import random

class XML_Interaction:
#        tree = ElementTree(file="./status/tasks.xml")
        solrFolder = "home/ubuntu/status/solrdata"
        topicFolder = "home/ubuntu/status/topicdata"
        dataFolder  = "~/data/xml"

        def update_task(self, taskid, status):
            """Updates individual task to new status number within XML task sheet
               
               Args:
                   tasid: The integer ID of the task to be modified
                   status: The string signifying the task status
               
               Returns: 
                   None
               
               Raises:
                   None                  
            """
           
            tasks = self.tree.findall("task")
            for task in tasks:
                children = task.getchildren()
                for child in children:
                    if child.tag == "status":
                        print "setting new status to " + str(status)
                        child.text = str(status)
                self.tree.write("outfile.xml")


        def check_task( self ):
            """Check through xml data to handle pending tasks

               Args:
                   None
                
               Returns:
                   None
 
               Raises:
                   None
            """
            tasks = self.tree.findall("task")
            for task in tasks:
                children = task.getchildren()
                for child in children:
                   if child.tag == "status":
                       return child.text

        def add_task( self, taskid, tasktype, folder=None ):
            """Add a task to the default xml task sheet
                
               Args:
                   taskid: unique ID for new task for tracking individual tasks
                   tasktype: Identifier to track purpose of task
                   folder: Name of output folder if necessary

               Returns:
                   None
    
               Raises:
                   None
            """
            if tasktype == "processSolr":
                if folder == None:
                    folder = self.solrFolder

                    root = self.tree.getroot()
                    newTask = SubElement( root, "task" )
                    newNode = Element( "status" )
                    newNode.text = "pending"
                    newTask.append( newNode )

                    newNode = Element( "taskid" )
                    newNode.text = str(taskid)
                    newTask.append( newNode )

                    newNode = Element( "directory" )
                    newNode.text = str(folder)
                    newTask.append( newNode )

                    self.tree.write("outfile.xml")

                elif tasktype == "processTopic":
                    print "Processing topic modeling data"
                    if folder == None:
                        folder = self.topicFolder
                else:
                    print "Unknown task" + tasktype

        def convert_XML(self):
            """Parses through a directory of NSF XML files starting a 
               conversion to Solr input format
                
               Args:
                   None
               
               Returns:
                   None
               
               Raises:
                   None
            """
            dir = os.path.expanduser( self.dataFolder )
            if os.path.isdir( dir ):
                d = os.listdir( dir )
                for file in d:
#                print "Parsing file %s" % file
                    if os.path.isfile( dir + "/" + file  ):
                        self.change_doc( dir, file )
                    else:
                        print dir+ "/" + file

        def create_solr_doc(self, info, status="private"):
            """Creates an in memory xml file for solr import under the format:
               dd_date nsf_id status summary description
        
               Args:
                   info: A list containing the data needed for solr doc
                   status: The public/private status of the prop                  
         
               Returns:
                   Returns a string of XML 
            """
            import xml.etree.ElementTree as xml
            import elementtree.ElementTree as ET
            from elementtree.ElementTree import XML, fromstring, tostring
            
            root = xml.Element("add")
            child = xml.Element("doc")
            root.append(child)
            
            field = xml.Element("field")
            field.attrib["name"] = "date"
            field.text = info[0]
            child.append(field)
            
            field = xml.Element("field")
            field.attrib["name"] = "id"
            field.text = info[1]
            child.append(field)
            
            field = xml.Element("field")
            field.attrib["name"] = "Project_Summary"
            field.text = info[3] 
            child.append(field)
            
            #only add status and full description if private
            if status == "private":
                field = xml.Element("field")
                field.attrib["name"] = "status"
                field.text = info[2]
                child.append(field)

                field = xml.Element("field")
                field.attrib["name"] = "Project_Description"
                field.text = info[4]
                child.append(field)
            
            return ElementTree.tostring(root, 'utf-8')
            
        def change_doc( self, path, name ):
            """Modifies original formated document from NSF to fit Solr format
               
               Args:
                   path: The path of the original document
                   name: The name of the original document

               Returns:
                   none
             
               Raises:
                   none
            """ 
            import xml.etree.ElementTree as xml
            import elementtree.ElementTree as ET
            from elementtree.ElementTree import XML, fromstring, tostring
            import time
            if name == "post.jar":
                return
                #tree = ElementTree( path + name )
                tree = ET.parse(path + "/" + name)
                root = tree.getroot()
                
                base = xml.Element("add")
                child = xml.Element("doc")
                base.append(child)
                 
                field = xml.Element("field")
                field.attrib["name"] = "id"
                ext = os.path.splitext(name)[1]
                if ext != ".xml":
                    return
                field.text = name[:-6]
                child.append(field)
                
                random.seed()
                priority = str( random.randint(0,4) )
                field = xml.Element("field")
                field.attrib["name"] = "status"
                field.text = priority
                child.append(field)
                
                summary = False
                tag_title = ""
                record = {}
                for ch in root.getiterator():     
                    if not (ch.tag in record ): #and ( record[ ch.tag ] == ch.text ) ) :
                        record[ ch.tag ] = ch.text
                        if ch.tag != "doc" and ch.tag != "add" and ch.tag != "DOCS" and ch.tag != "DOCUMENT":
                            if ch.tag == "Section_Title" and ( ch.text == "Project Summary" or ch.text == "Project Description" ):                                   
                                summary = True
                                if ch.text == "Project Summary":
                                    tag_title = "Project_Summary"
                                if ch.text == "Project_Description":
                                    tag_title = "Project_Description"                                
                            elif summary == True:
                                if ch.tag == "DRECONTENT":
                                    field                = xml.Element("field")
                                    field.attrib["name"] = tag_title
                                    field.text           = ch.text 
#                                print "Adding Element[%s], name[%s],\ntxt[%s]" % (field, field.attrib, field.txt)
#                                        print field.attrib
#                                        print field.txt
                                    child.append(field)
                                    summary = False
                            else:				
                                if ch.tag != "DRECONTENT":
                                    field                = xml.Element("field")
                                    field.attrib["name"] = ch.tag
                                    field.text           = ch.text
                                    child.append(field)
                                   # print "Adding Element[%s], name[%s],\ntxt[%s]" % (field, field.attrib, field.txt)
		
                file_n = path + "/mod/mod_" + name
                #print "New file = %s" % file_n                 
                file = open( file_n, 'w' )
                xml.ElementTree(base).write(file)
                file.close()

                #for task in tasks:                     
                #       children = task.getchildren()
                #       for child in children:
                #               if child.tag == "status":
                #                       print "setting new status to " + str(status)
                #                       child.text = str(status)
        #def checkTask( self, taskid ):

