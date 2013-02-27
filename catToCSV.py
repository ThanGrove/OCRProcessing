# coding=utf-8

###################  ###########################
#
#   
###############################################################

from os.path import dirname, join
from THLXml import Catalog
from codecs import open
import sys
import time

args= {}

my_path = dirname(__file__)
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')
cat = Catalog.Catalog(catpath, 'Peltsek')
tlist = cat.getTextList()

outfile = join(my_path, 'out', 'peltsek-textlist.csv')

sys.stdout = open(outfile, 'w', encoding='utf-8')

for t in tlist:
  outline = ""
  for i in t:
    if i is not None:
      i = i.replace('\r','')
      i = i.replace('\n','')
      outline += i + ","
  print outline[0:-1] # removes the comma at the end