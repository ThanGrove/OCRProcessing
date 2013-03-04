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

cat.importVolInfo(join('data', 'ngb-pt-vols.xml'))

outfile = join(my_path, 'out', 'ngb-pt-vols.xml')

#sys.stdout = open(outfile, 'w', encoding='utf-8')

cat.write(outfile, 'vols')