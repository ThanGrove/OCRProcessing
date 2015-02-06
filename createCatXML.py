# coding=utf-8

###################  ###########################
#
#   
###############################################################

from os.path import dirname, join
from THLXml import Catalog, Functions
from codecs import open
import sys
import time

args= {}

my_path = dirname(__file__)
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')
cat = Catalog.Catalog(catpath, 'Peltsek')

cat.import_vol_info(join('data', 'ngb-pt-vols.xml'))
dt = Functions.getDateTime()
outfile = join(my_path, 'out', 'ngb-pt-cat_{0}.xml'.format(dt))

print "Writing new catalog to {0}".format(outfile)
#sys.stdout = open(outfile, 'w', encoding='utf-8')

cat.write(outfile, 'vols')