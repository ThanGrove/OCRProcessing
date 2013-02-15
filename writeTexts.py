# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.
#
# Can call with start={num} or end={num} or texts={num,num,num, i.e. commaseparated numbers}
#

from os.path import dirname, join
from THLXml import Catalog
import sys

args= {}

def writeText(t, tnum, path, typ):
  print "in write text: {0}".format(typ)
  if typ == "bibl" or typ == "both":
    print "Writing {0} Tibbibl!".format(str(tnum))
    tid = "ngb-pt-{0}-bib".format(str(tnum).zfill(4))
    t.set("thlid", tid)
    t.writeTextBibl(path)
  if typ == "text" or typ == "both":
    print "Writing {0} Text!".format(str(tnum))
    tid = "ngb-pt-{0}-text".format(str(tnum).zfill(4))
    t.set("thlid", tid)
    t.writeText(path)
    
for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

my_path = dirname(__file__)

# Set up Peltsek Catalog with vol data.
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')   
cat = Catalog.Catalog(catpath, 'Peltsek')
cat.importVolInfo(join('data', 'ngb-pt-vols.xml'))

if not args.has_key('path'):
  args['path'] = 'out'
  
if not args.has_key('type'):
  args['type'] = 'both'
  
if args.has_key('texts'):
  txts = args['texts'].split(',')
  for tnum in txts:
    tnum = tnum.strip()
    txt = cat.getText(tnum)
    if txt:
      writeText(txt, tnum, args['path'], args['type'])
else:
  tstnum = int(args['start']) if args.has_key('start') else 1
  tennum = int(args['end']) if args.has_key('end') else int(cat.textcount)
  for t in cat.iterTexts():
    tnum = int(t.key)
    if tnum >= tstnum and tnum <= tennum:
      writeText(t, tnum, args['path'], args['type'])
      
