#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  xml_client.py
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
#requires ElementTree

from xml_parser import XML_Interaction
import time

def main():
        """
        taskid = 0
        xParser = XML_Interaction()
        xParser.add_task( taskid, "processSolr" )       
        i = 0
        time.sleep(10)
        xParser.update_task(0, "processed")
        status = "idle"
        while status != "shutdown":
                time.sleep(5)           
                status = xParser.check_task()
                print str(status)
                i = i + 1
                if i == 3:
                        xParser.update_task(0, "shutdown")
        """
        xParser = XML_Interaction()

        xParser.convert_XML()

        return 0


if __name__ == '__main__':
        main()

