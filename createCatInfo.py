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

cat.import_vol_info(join('data', 'ngb-pt-vols.xml'))


outfile = join(my_path, 'out', 'ngb-pt-vol-dox.txt')

#sys.stdout = open(outfile, 'w', encoding='utf-8')

fout = open(outfile, 'w', encoding='utf-8')
print cat.vols.keys()
for k in cat.vols.keys():
  print "Doing volume {0}".format(k)
  v = cat.get_volume(k)
  fout.write(v["dox"] + "\n")
  
fout.close()