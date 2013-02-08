# coding=utf-8
import sys
import codecs
import xml.etree.ElementTree as ET  # See http://docs.python.org/2/library/xml.etree.elementtree.html

def printUsage():
  """Print out usage instructions"""
  print "\nparseXML.py - A script to test xml parsing returns designated page's text!\n"
  print "Usage:"
  print "\tparseXML.py {file name} {page number}\n"
  
# Get commandline parameters
fname = sys.argv[1]
pstr = sys.argv[2]

foutname = 'output1.txt'


# Valiate and read-in the file
try:
  pnum = int(pstr)
  tree = ET.parse(fname)
  root = tree.getroot()
  
  #print "Root is: " + root.tag
  
  milestones = root.findall(".//milestone")
  #print "There are {0} milestones in the document!".format(len(milestones))
  
  div1 = root.find(".//div1")
  #print div1
  
  fout = codecs.open(foutname, 'w', encoding='utf-8')
  print "Writing text of page {0}".format(pstr)
  for e in div1.iter():
    n = e.get('n')
    if n != None and n.startswith(pstr):
      print n,
      if e.tail != None:
        fout.write(unicode(e.tail))
  
  #print it
  #txt = ms.tail
  
  #fout.write(unicode(txt))
  #fout.close()
  
except IOError:
  print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(fname)
  printUsage()


