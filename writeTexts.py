# coding=utf-8

###################  writeTexts.py ###########################
#
#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.
#
#    Usage:
#         python writeText.py type={bibl|text|both} path={path} start={num} end={num} texts={##,##,##,...}
#     
#           All params option:
#               type = type of output (bibliographic record or full text)
#               path = path to output folder that is subfolder of "out"
#               start = the number of the text to start with
#               end = the number of the text to end with
#               texts = a comma-separated list of individual texts to process instead of start and end
#
###############################################################

from os.path import dirname, join
from THLXml import Catalog
import sys
import time

args= {}

# Function that takes a text, output path, and type and writes that type of text file
def writeText(t, tnum, path, typ):
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
    
# Split args into a hash
for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

if not args.has_key("type"):
  args["type"] = "both"
  
my_path = dirname(__file__)

# Redirect sysout to a dated log
trange = "_all_"
if args.has_key("start"):
  trange = "_" + args["start"] + "-"
  if args.has_key("end"):
    trange += args["end"]
  else:
    trange += "end"
  trange += "_"
if args.has_key("texts"):
  trange="_custom_"
  
ltime = time.localtime(time.time())
datearr = [str(ltime[0]), str(ltime[1]).zfill(2), str(ltime[2]).zfill(2)]
timearr = [str(ltime[3] - 5).zfill(2), str(ltime[4]).zfill(2), str(ltime[5]).zfill(2)]
dtstr = "-".join(datearr) + "-" + "".join(timearr)
logfile = join(my_path,"logs","conv_{0}{1}{2}.log").format(args["type"],trange, dtstr)
print "logfile is: {0}".format(logfile)
sys.stdout = open(logfile, 'w')
print 'Log file for Peltsek conversion'
print 'arguments: {0}'.format(args)

# Load Peltsek Catalog with vol data.
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')   
cat = Catalog.Catalog(catpath, 'Peltsek')
cat.importVolInfo(join('data', 'ngb-pt-vols.xml'))

if not args.has_key('path'):
  args['path'] = join(my_path, 'out')
else:
  args['path'] = join(my_path, 'out', args['path'])
  
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
      
