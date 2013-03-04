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
cat.importVolInfo(join('data', 'ngb-pt-vols.xml'))

outpath = join(my_path, 'out', 'peltsek-paginations.csv')

fout = open(outpath, 'w', encoding='utf-8')

for t in cat.iterTexts():
  ln = t.key + "," + t.startpage + "," + t.endpage + "\n"
  fout.write(ln)
  
fout.close()