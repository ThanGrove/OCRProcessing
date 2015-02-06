# coding=utf-8

#   A script to iterate through a catalog XML file and make sure there are no
#     gaps in the pagination.

import os
from os.path import abspath, dirname, join
import codecs
import re
import sys
from lxml import etree
from THLXml import Catalog, OCRVolume, Text, Functions

my_path = abspath(dirname(__file__))
print "mypath is: {0}".format(my_path)

datafolder = join(my_path, '..', 'data')

# Find latest pelstek-with-lines_{date} file and use that for the source catfile
pwlfiles = []
for f in os.listdir(datafolder):
  if "peltsek-with-lines_" in f:
    pwlfiles.append(f)
pwlfiles.sort()
lastpwlfile = pwlfiles[-1]
catfileName = lastpwlfile #'peltsek-with-lines_2013-03-21-154826.xml' Or customize which file to use here

# Set cat and folder and out paths
catpath = join(datafolder, catfileName)             # Path to the catalog data
volfolder = join(my_path, '..', 'volsource')         # Folder where vol OCR resides
dt = Functions.getDateTime()
outpath = join(my_path, '..', 'output', 'peltsek-page-issues_' + dt + '.log')   # Path to write new catalog

print "The output file is at: {0}".format(outpath)

# Instantiate the Peltsek Catalog
cat = Catalog.Catalog(catpath, 'Peltsek')

cat.import_vol_info(join(datafolder, 'ngb-pt-vols.xml'))

tlist = []
dct = 0
out = codecs.open(outpath, 'w', encoding='utf-8')

out.write("************ Pagination Checking for Pelstek Catalog ****************\n")
out.write("Catalog XML File: {0}\n***********************************\n\n".format(catfileName))

for txt in cat.iter_texts():
  tlist.append([txt.key, txt.vnum, txt.startpage, txt.endpage])

# Go through Text list and find where previous [ptext] end page and this [txt] start page are not sequential
for n in range(len(tlist)):
  txt = tlist[n]
  if n > 0:
    ptext = tlist[n - 1]
    seq = 1 # is it sequential assume 1 = yes
    # If previous text is in the same volume
    if ptext[1] == txt[1]:
      # if ending page of previous text does not match start page of this text
      if ptext[3] != txt[2]:
        # if prev text end page doesn't end in .6 or this start page doesn't have .1
        if ".6" not in ptext[3] or ".1" not in txt[2]:
          seq = 0
        # or if prev text end page is not one less than this texts start page
        elif int(float(ptext[3])) + 1 != int(float(txt[2])):
          seq = 0
    elif int(float(txt[2])) > 1:
      out.write("Text {0} is first text of vol {1} but starts on page {2}\n".format(txt[0], txt[1], txt[2]))
      dct += 1

    if seq == 0:
      out.write("Discrepancy between text {0} (endpage: {1}) and text {2} (startpage: {3}) in volume {4}\n".format(ptext[0], ptext[3], txt[0], txt[2], txt[1]))
      dct += 1

out.write("\n--------------------------------------\nThere were {0} discrepencies.\n".format(dct))

print "There were {0} discrepencies.".format(dct)
out.close()

  