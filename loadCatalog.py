# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.

import os
import codecs
import re
from lxml import etree
from OCRXml import *

sep = os.sep
datafolder = '..{0}data{0}'.format(sep)
catpath = datafolder + 'peltsek.xml'              # Path to the catalog data
volfolder = '..{0}source{0}'.format(sep)          # Folder where vol OCR resides
catout = datafolder + 'peltsek-with-lines.xml'    # Path to write new catalog
vol3src = volfolder + 'nying-gyud-vol03_than_ygNTCyzRdq4u.txt'
# Instantiate the Peltsek Catalog
cat = XMLCatalog.Catalog(catpath, 'Peltsek')

tc = 0
for v in cat.vols:
  vl = cat.vols[v]
  tc += len(vl['texts'])

print cat.vols[3]

