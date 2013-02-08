# coding=utf-8
import sys
import codecs
from lxml import etree
# import xml.etree.ElementTree as ET  # See http://docs.python.org/2/library/xml.etree.elementtree.html

#### XMLCat Class   ####
class XMLCat:
  """A class for processing an XML document that is a list of texts.
     The XML expected here is based on the simple schema for mapping from an Excell document, Peltsek_Excell_Datamap.xsd
     This is a <spreadsheet> element with a series of <textrecord>s in it. Each text record has the following children:
       tnum, title, vnum, startpage, endpage, numofchaps, chaptype, doxography, translators, crossrefs, notes """
  
  docpath = ""
  
  def __init__(self, path):
    
    
#### End of XMLCat Class ###

#### Functions ####
def printUsage():
  """Print out usage instructions"""
  print "\nparseXML.py - A script to test xml parsing returns designated page's text!\n"
  print "Usage:"
  print "\tparseXML.py {file name} {page number}\n"
  
# Fields in XML:
#      tnum title vnum startpage endpage numofchaps chaptype doxography translators crossrefs notes
def parseCatalog(path):
  """Takes a path to an XML document and returns a dictionary of {vols, texts},
      where vols = an dictionary of volumes and texts a dictionary of texts,
      each values of the vols dictionary are an array of text numbers in that volume
      text numbers are absolute numbers from the beginning of the catalog 1, 2, ..."""
  try:
    tree = etree.parse(path)
    root = tree.getroot()
    rows = root.xpath('/*//textrecord')
    vols = {}
    texts = {}
    for r in rows:
      vnum = r.find('vnum').text
      mytnum = r.find('tnum').text
      pt = r.itersiblings(tag='textrecord', preceding=True)
      tnum = len(list(pt)) + 1
      if vnum in vols:
        vols[vnum].append(tnum)
      else:
        vols[vnum] = [tnum]
      texts[tnum] = r
    
    print "Peltsek has {0} volumes and {1} texts".format(len(vols), len(texts))
    
  except IOError:
    print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(fname)
    
  return {"volumes":vols, "texts":texts }
  
def writeText(t, wf):
  """Writes text info from t into the unicode file wf"""
  print "Writing text {0}!".format(t.find('tnum').text)
  vnum = t.find('vnum').text
  st = t.find('startpage').text
  if st == None:
    st = "0"
  en = t.find('endpage').text
  if en == None:
    en = "0"
  wf.write( t.find('tnum').text + "|" + t.find('title').text +
              "|" + t.find('vnum').text + "|" + st +
              "|" + en  +  chr(13))

def writeVolumes(vd, fo):
  """Output a list of Volumes"""
  for k in sorted(vd.iterkeys()):
    v = vd[k]
    print "doing {0}!".format(k)
    fo.write("*_*_*_*_*_* {0} *_*_*_*_*_* {1}".format(k, chr(13)))
    for t in v:
      fo.write( "\t{0}{1}".format(t, chr(13)) )
         
######### MAIN ROUTINE ##########
# Get commandline parameters

def main():  
  fname = sys.argv[1]
  fpath = sys.argv[2]
  #foutname = '../output/testout.txt'
  
  cat = parseCatalog(fpath + fname)
  
  print len(cat["volumes"].keys())
  print cat["texts"].has_key(64)
  
  #fout.close()

######## End of Main Routine #######

# Call Main
main();

