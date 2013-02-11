# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.

import os
import codecs
import re
from lxml import etree
from THLXml import *

sep = os.sep
datafolder = '..{0}data{0}'.format(sep)
catpath = datafolder + 'peltsek.xml'              # Path to the catalog data
volfolder = '..{0}source{0}'.format(sep)          # Folder where vol OCR resides
catout = datafolder + 'peltsek-with-lines.xml'    # Path to write new catalog
vol3src =  volfolder + 'nying-gyud-vol03_than_ygNTCyzRdq4u.txt'
# Instantiate the Peltsek Catalog
cat = XMLCatalog.XMLCat(catpath, 'Peltsek')

# Iterate through the volume ocr files in the given folder
for f in os.listdir(volfolder):
  
  # Determine volume info
  m = re.search('\-vol(\d+)\_', f)
  vnum = int(m.group(1))             # volume number
  volpath = volfolder + f            # volume doc path
  vol = OCRVolume.Vol(volpath, vnum)  # read in the vol and create object
  vtxtlist = cat.getVolumeTOC(vnum, 'list') # get text list for vol from catalog
  lasttext = 0
  
  # Iterate through texts in the volume
  for t in vtxtlist:                  
    mystpg = t['start']
    newstpg = mystpg
    tnum = int(t['key'])
    txt = cat.getText(tnum, 'element')
    if mystpg != None and txt != None:
      lnum = vol.textStartLine(mystpg)  # Find and assign start line for text
      if lnum == False:
        lnum = '1'
      newstpg += '.' + lnum
      cat.getText(tnum, 'element').find('startpage').text = newstpg
      
      # Determine end line for previous text and assign
      if lasttext != 0:
        lep = cat.getText(lasttext,'element').find('endpage').text
        if lep != None:
          if vol.textStartsAtTop(mystpg):
            lep = str((int(lep) - 1)) + ".6"
          else:
            lep += '.' + lnum
          cat.getText(lasttext,'element').find('endpage').text = lep
      lasttext = tnum
      
  # Write out the catalog file with updated line numbers
cat.write(catout)