# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.

from os.path import dirname, join
from THLXml import *
import sys
from codecs import open

args= {}

for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

my_path = dirname(__file__)
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')
cat = Catalog.Catalog(catpath, 'Peltsek')
cat.import_vol_info(join('data', 'ngb-pt-vols.xml'))

for t in cat.iter_texts("xml"):
  print type(t)
  print t.find('startpage').text
  sys.exit(0)

outpath = join(my_path, 'out', 'ngb-pt-titles_wylie_new.txt')

## Write vol bibs
#cat.write(join("out", "vols"), "volbibs")

#fout = open(outpath, 'w', encoding='utf-8')

for t in cat.iter_texts():
  print t.key, 
  #fout.write(cat.tibToWylie(t.title) + "\n")
#  ln = t.key + "," + t.startpage + "," + t.endpage + "\n"
  
#fout.close()