# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.

import os
from os.path import dirname, join
import codecs
import re
import sys
from lxml import etree
from THLXml import Catalog, OCRVolume, Text, Functions

my_path = dirname(__file__)
datafolder = join(my_path, '..', 'data')
catpath = join(datafolder,'peltsek.xml')             # Path to the catalog data
volfolder = join(my_path, '..', 'volsource')         # Folder where vol OCR resides
dt = Functions.getDateTime()
catout = join(datafolder, 'peltsek-with-lines_' + dt + '.xml')   # Path to write new catalog

# Instantiate the Peltsek Catalog
cat = Catalog.Catalog(catpath, 'Peltsek')

# Iterate through the volume ocr files in the given folder
for f in os.listdir(volfolder):
  
  # Determine volume info
  m = re.search('\-vol(\d+)\_', f)
  vnum = int(m.group(1))             # volume number
  volpath = join(volfolder, f)           # volume doc path
  print "Doing volume {0}".format(vnum)
  try:
    vol = OCRVolume.Vol(volpath, vnum)  # read in the vol and create object
    vtxtlist = cat.getVolumeTOC(vnum, 'list') # get text list for vol from catalog
    lasttext = 0
    
    # Iterate through texts in the volume
    for t in vtxtlist:                  
      mystpg = t['start']
      if mystpg != None and "." in mystpg:
        pts = mystpg.split(".")
        mystpg = pts[0]
      newstpg = mystpg
      tnum = int(t['key'])
      txt = cat.getText(tnum, 'element')
      if mystpg != None and txt != None:
        lnum = vol.textStartLine(mystpg)  # Find and assign start line for text
        if lnum == False:
          lnum = '1'
        newstpg += '.' + lnum
        cat.getText(tnum, 'element').find('startpage').text = newstpg
        
        # Set end line for previous text based on this text's beginning
        if lasttext != 0:
          lep = cat.getText(lasttext,'element').find('endpage').text
          if lep != None:
            if "." in lep:
              pts = lep.split(".")
              lep = pts[0]
            if vol.textStartsAtTop(mystpg):
              lep = str((int(mystpg) - 1)) + ".6"
            else:
              lep += '.' + lnum
            cat.getText(lasttext,'element').find('endpage').text = lep
        lasttext = tnum
        
    # Set end page of last text in volume
    ltnum = vtxtlist[-1]['key']
    ltext = cat.getText(ltnum, 'element')
    endpg = ltext.find('endpage').text
    if endpg == None:
      endpg = vtxtlist[-1]['end']
    if endpg is not None and "." not in endpg:
      endpg = endpg + ".6"
    ltext.find('endpage').text = endpg
    
  except etree.XMLSyntaxError:
    print "XML Error for volume {0}".format(vnum)
  #except Exception:
  #  print "Generic error for volume {0}".format(vnum)
  #  print sys.exc_info()
  #  sys.exc_info()[2].print_stack()
    
# Run routine to fix missing paginations
cat.fixMissingPaginations()

# Run final check to fix problem where one text ends at e.g. 95.1 and next text starts 96.1
# Assume that 95.1 should be 95.6
prevTxt = None
for txt in cat.iterTexts("xml"):
  if prevTxt is not None:
    tst = txt.find('startpage')
    ptend =  prevTxt.find('endpage')
    if tst is not None and ptend is not None:
      if ".1" in tst.text and ".1" in ptend.text:
        if int(float(tst.text)) == int(float(ptend.text)) + 1:
          ptend.text = str(int(float(ptend.text))) + ".6"
  prevTxt = txt

# Write out the catalog file with updated line numbers
cat.write(catout)