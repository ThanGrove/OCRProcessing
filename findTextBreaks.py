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
catpath = datafolder + 'peltsek.xml'
volfolder = '..{0}source{0}'.format(sep)
volpath =  volfolder + 'nying-gyud-vol02_than_KD5jc1bUVeUZ.txt'

# Open test out file and run test commands
foutname = '..{0}output{0}'.format(sep)

#print type(XMLVars.XMLCommonVars)

# Instantiate the Peltsek Catalog
cat = XMLCatalog.XMLCat(catpath, 'Peltsek')
#fnm = "testout.xml"
#fout = codecs.open(fnm, 'w', encoding='utf-8')
#t = cat.getText(534, 'element')

#fout.write(etree.tostring(t, encoding=unicode))
#print THLXml.tibToWylie

a = []
for f in os.listdir(volfolder):
  m = re.search('\-vol(\d+)\_', f)
  vnum = int(m.group(1))
  volpath = volfolder + f
  vol = OCRVolume.Vol(volpath, vnum)
  vtxtlist = cat.getVolumeTOC(vnum, 'list')
  for t in vtxtlist:
    mystpg = t['start']
    tnum = int(t['key'])
    txt = cat.getText(tnum, 'element')
    if mystpg != None and txt != None:
      lnum = vol.textStartLine(mystpg)
      if lnum == False:
        lnum = '1'
      mystpg += '.' + lnum
      cat.getText(tnum, 'element').find('startpage').text = mystpg
    #print "{0}:{1}:{2}".format(t['key'], mystpg, vol.textStartLine(mystpg))
    
    
print cat.getText(4, 'element').find('startpage').text

print cat.getText(54, 'element').find('startpage').text


print cat.getText(123, 'element').find('startpage').text