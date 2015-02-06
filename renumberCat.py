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
cat.renumber_texts()
outpath = join(my_path, 'data', 'peltsek-with-lines_renumbered.xml')
cat.write(outpath)
print "Texts renumbered and catalog written to {0}".format(outpath)