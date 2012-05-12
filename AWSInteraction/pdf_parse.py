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
#  

import os
import subprocess
import re
import time
import sys

class PDF_Parse:
	pdf_exe              =""
	pdftk_exe            =""
	datapath             = os.path.expanduser("~/data/2012-03-17/pdf/")
	outputpath           =""
	awards               = { "init":"init"}
	
	def __init__(self):
		self.pdf_exe     = "pdftotext"
		self.pdftk_exe   = "pdftk"
		self.outputpath  = os.path.expanduser("~/tmp/output/")	
		
		
	def run_conversion(self, _opath = outputpath ):		
		if _opath == "":
			_opath = os.path.expanduser("~/tmp/output/")
			
		self.make_structure( _opath )
			
		#locate all files in path, extract award name and store in award array
		files = os.listdir( self.datapath )
		for file in files:
			#print "File: %s" % file
			award = re.search('[0-9]{7}', file)
			#print "Award: %s" % award.group(0)
			sys.stdout.write(".")

			#print "setting %s to notoc" % award.group(0)
			self.awards[ (award.group(0) + "RC.txt") ] = "notoc" 
			#print "\tVerification: %s = %s" % ( award.group(0), self.awards[ (award.group(0) + "RC.txt") ] )

			ofile = _opath + award.group(0) + "RC.txt"
			test = os.popen(self.pdf_exe + " -layout -eol unix -nopgbrk %s%s %s" % ( self.datapath, file, ofile ) )
			
		print "\n"
		
		self.sort_TOC( _opath )
	
	
	
	def sort_TOC(self, search_path ):
			notoc = "../notoc/"
			toc   = "../toc/"
			
			results = os.popen( "grep TABLE %s*.txt" % search_path )
			
			for result in results:
				fname_result = re.search('[0-9]{7}', result)
				fname = fname_result.group(0) + "RC.txt"
				self.awards[fname] = "toc"
				#print "award %s set to toc" % fname
				
				os.popen( "cp -p %s %s" % (search_path + fname, search_path + toc) )
				#print "cp -p %s %s" % (search_path + fname, search_path + toc) 
				#print "Result[%s]" % result							
			
			for award in self.awards:
				if self.awards[award] == "notoc":
					os.popen( "cp -p %s %s" % (search_path + award, search_path + notoc ) )
					#print "cp -p %s %s" % (search_path + award, search_path + notoc)			
			
			
			
			print "Files found with Table of Contents:\n\t"  
			print "ls -1 %s | wc -l" % (search_path + toc)
			files = os.popen( "ls -1 %s | wc -l" % (search_path + toc) ) 
		
			for string in files:
				print string
				
			print "Files found without Table of Contents:\n\t"
			print "ls -1 %s | wc -l" % (search_path + notoc)
			files = os.popen( "ls -1 %s | wc -l" % (search_path + notoc) )	
			
			for string in files:
				print string
			
			print "Removing header up to electric signature"
			self.remove_to_sig( search_path + notoc )
			self.remove_to_sig( search_path + toc )
			
	def make_structure(self, opath):
		d = os.path.dirname( opath )
		notoc = d + "/../notoc"
		toc   = d + "/../toc"
		
		if not os.path.exists(d):
			print "Creating directory %s" % opath
			os.makedirs(d)			
		else:
			print "Outputting files to %s" % opath
		
		#create directory for no table of contentsor delete previous contents
		if not os.path.exists( notoc ):
			print "Creating directory %s", notoc
			os.makedirs( notoc )
			os.makedirs( notoc + "/header")
			os.makedirs( notoc + "/main")
		else:
			if os.path.exists( notoc + "/*.txt" ):
				os.remove( notoc + "/*.txt" )
			
		#create directory for table of contents or delete previous contents
		if not os.path.exists( toc ):
			print "Creating directory %s", toc
			os.makedirs( toc )
			os.makedirs( toc + "/header")
			os.makedirs( toc + "/main"  )
			
		else:
			if os.path.exists( toc + "/*.txt" ):
				os.remove( toc + "/*.txt" )					    
	    
		bkp = os.path.dirname( opath + "bkp/")	
		print bkp
		if not os.path.exists(bkp):
			os.makedirs(bkp)
				
		print "Moving old files to backup directory"
		os.popen( "mv %s*.txt %s/." % (opath, bkp) )
		time.sleep(1)
		print ("mv %s*.txt %s/." % (opath, bkp) )
		os.popen( "tar -cvzf %s/backup_%s.tar.gz %s/*.txt" % (bkp, time.time(), bkp ) )
		print "Tarring files for backup:\n\t tar -cvzf %s/backup_%s.tar.gz %s/*.txt" % (bkp, time.time(), bkp )
		time.sleep(1)
		print ( "tar -cvzf %s/backup_%s.tar.gz %s/*.txt" % (bkp, time.time(), bkp ) )
		os.popen( "rm -r %s*.txt" % opath )
		"""

	def remove_to_sig(self, directory):
		#initial search, defaulting to sig
		search_string = "RAPID"
						 
		#locate all files in path
		folder = os.listdir( directory )
		for file in folder:
			if not os.path.isdir(directory + file):
				print "current file: \n\torig[%s]\n\theader[%s]\n\tmain[%s]" % ( directory+file, directory + "header_" + file, directory + "main_" + file) 
				try:
					f       = open( directory + file, "r" )
				except:
					print "Could not open originally file %s" % directory + file
					break
				try:
					fheader = open( directory + "header/" + file, "w")
				except:
					print "Could not open header file %s" % directory + "header/" + file
					f.close()
					break
				try:					
					fbody   = open( directory + "main/" + file, "w")			
				except:
					print "Could not open main file %s" % directory + "main/" + file
					f.close()
					fheader.close()
					break
					
				line = f.readline()
				
				#While we haven't hit the end of the signature or the end of the file
				while not line.find(search_string) == '-1' and not line == "":
					#print "Line = %s" % line
					fheader.write( line )
					line = f.readline()
				#count = 0
				if line == 0:
					print "End of document found, no signature present"
				else:	
					print "sig end found: %s" % line	
					while not line == "":
						fbody.write( line )
						line = f.readline()
						#count += 1
						#print "%s: %s" % ( count, line)
				f.close()
				fheader.close()
				fbody.close()
			else:
				print "Directory found: %s" % file
def main():
	parse_obj = PDF_Parse()
	parse_obj.run_conversion()
		
		
if __name__ == '__main__':
	main()
