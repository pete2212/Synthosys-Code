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
import pysftp
import tarfile

class NetInteraction:
	srv = None
	
	def netConnect(self, address, key = "~/.ssh/automation-key2.pem", user="ubuntu"):
		try:
			print "Host: %s, Username %s, Private Key %s" % (address, user, key)
			self.srv = pysftp.Connection( host = address, username = user, private_key = key )	
#			self.srv.put("test.txt", "test_out.txt")
#			self.srv.get("test_out.txt", "return_test.txt")
		
		except:
			raise

#	def uploadFolder(self, dirpath):
		#try:
#			fcount = 0
#			listing = os.listdir(dirpath
#			for infile in listing:
#			if fcount >= 1000:
#				count = 0
#				zipName = zipName + "_" + count
				 	
#		except:
#			raise

        def upload( self, path, oname ):
                try:
                        print "Uploading"
                        self.srv.execute("mkdir data")
                        self.srv.put(path, oname)
                        print "Finished"
                except:
                        raise
def main():
        import sys
        #arg 2 = ip
        if len(sys.argv) > 1:
                ip = sys.argv[1]
                con = NetInteraction()
                con.netConnect(ip)                
                con.upload("/home/ptr/workgroup/python/upload/2012-03-17.tar.gz", "/home/ubuntu/data/data.tar.gz")
        else:
                print "Supply ip address"

if __name__ == '__main__':
        main()
