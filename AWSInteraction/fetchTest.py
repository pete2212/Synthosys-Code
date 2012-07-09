import unittest
import pyFetch
import os
import sys


class FetchTestCase(unittest.TestCase):
    """Class to test data migration class and solr import functionality
    """
    WRITE_PATH = "/home/ptr/data/2012-05-15/"
    XML_FILE_NAME = "solr_xml_test.xml"
    XML_EXT_NAME = "xml_extension_test.xml"
    NWF_EXT_NAME = "nwf_extension_test.nwf"
    PDF_EXT_NAME = "pdf_extension_test.pdf"

    def setUp(self):      
        """A function to setup the environment for testing
          
           Args:
               None
 
           Returns:
               None
     
           Raises:
               None
        """
        self.test = pyFetch.ImportProp()
        
        #generate 3 files for testing locate function
        self.xmlname = self.WRITE_PATH + self.XML_EXT_NAME
        self.touch(self.xmlname)
        f = open(self.xmlname, 'w')
        f.write("xml_test")
        f.close()
        self.nwfname = self.WRITE_PATH + self.NWF_EXT_NAME
        self.touch(self.nwfname)
        f = open(self.nwfname, 'w')
        f.write("nwf_test")
        f.close()
        self.pdfname = self.WRITE_PATH + self.PDF_EXT_NAME
        self.touch(self.pdfname)
        f = open(self.pdfname, 'w')
        f.write("pdf_test")
        f.close()
#self.addTest(FetchTestCase('test_locate'))        
        
    def touch(self, fname):
        with file(fname, 'a'):
            os.utime(fname, None)

    def test_locate(self):
        """Attempts to locate 3 test files, one each of xml, pdf and nwf
        """
        print "testing location function"
#        xmlname = self.WRITE_PATH + self.XML_EXT_NAME
#        self.touch(xmlname)
#        nwfname = self.WRITE_PATH + self.NWF_EXT_NAME
#        self.touch(nwfname)
#        pdfname = self.WRITE_PATH + self.PDF_EXT_NAME
#        self.touch(pdfname)
               
        result = self.test.get_prop(self.xmlname) 
        print result
        result = self.test.get_prop(self.nwfname)
        self.assertEqual(result[0], True)
        print result
        self.assertEqual(result[0], True)
        result = self.test.get_prop(self.pdfname)
        print result
        self.assertEqual(result[0], True)

    def generate_xml_file(self):
        print "xml file generation coming soon" 
 
    def tearDown(self):
#        self.test.dispose()
#        self.test = none
        if os.path.isfile(self.XML_EXT_NAME):
            os.remove(self.XML_EXT_NAME)
        xmlname = self.WRITE_PATH + self.XML_EXT_NAME
        if os.path.isfile(xmlname):
            os.remove(xmlname)
        nwfname = self.WRITE_PATH + self.NWF_EXT_NAME
        if os.path.isfile(nwfname):
            os.remove(nwfname)
        pdfname = self.WRITE_PATH + self.PDF_EXT_NAME
        if os.path.isfile(pdfname):
            os.remove(pdfname)
        print "removing pdf output file"
        if os.path.isfile("/home/ptr/data/pdf_archive/11111.pdf"):
            os.remove("/home/ptr/data/pdf_archive/11111.pdf")

       
    def test_solr_db_add(self):
        """Attempts to push a message to sql database to verify format
        """
#        print "push too few entries for testing"
#        entry = ["11111", "11/10/1981", "summary", "description"]
#        self.test.add_solr_db(entry)

        entry = ["11111", "11/10/1981", "summary", "description", "status"]
        #make sure entry doesn't already exist
        self.test.remove_id_solr_db("11111")
        self.test.add_solr_db(entry)

#        print "push too many entries for testing"
#        entry = ["11111", "11/10/1981", "summary", "description", "status", "baddata" ]
#        self.test.add_solr_db(entry)

    def test_solr_srv_add(self):
        #nsf_id, date, "summary", "description", "status"
        entry_type = "memory" 
        self.test.remove_id_solr_db("22222")
        entry = ["22222", "10/21/1981", "summary", "description", "status"]
        self.test.add_solr_entry(entry, entry_type)
#        self.test.add_solr_file(fname)

    def in_memory_xml(self):
        """
        """
        print "memory test coming soon"    
     
    def test_move_and_tar_test(self):
        """Moves dummy files to new directory and attempts to add to tar

           Args:
               None
 
           Returns:
               None

           Raises:
               None
        """
        #nsf_id/dd_date/summary/description
        print "move and tar test"
        entry = ["11111", "12/12/2012", "summary", "description"]
        pdfname = self.WRITE_PATH + self.PDF_EXT_NAME
        location = [True, True, pdfname, False, "", False, ""]
                
        self.test.move_found_data(entry, location)

    def build_solr_entry(self):
#self.test.pull_solr_info()
        pass

if __name__ == '__main__':
    unittest.main()
#if len(sys.argv) > 1 and sys.argv[1] == "test":
#    u = unittest.TestSuite()
#    u.addTest(FetchTestCase('test_locate'))
    #result = unittest.TestResult()
#else:
#    print "Please input correct parameter"
