# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.
#
#   Usage:
#           testTextBreaks.py vol=#
#

from os.path import dirname, join
from os import listdir
import sys
from codecs import open
from THLXml import *
import time
from re import search

my_path = dirname(__file__)
textdelims = {u'རྒྱ་གར་སྐད་':0, u'བོད་སྐད་':0, u'རྫོགས་སོ':0, u'་ཕྱག་འཚལ':0, u'བཞུགས་':0, u'ཞེས་བ':0}

def searchForBreak(stline):
  found = 0
  for delim in textdelims:
    if stline.find(delim) > -1:
      textdelims[delim] += 1
      found = 1
  return found
  
# Parse arguments into hash
args= {}
for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

# Set log file
ltime = time.localtime(time.time())
datearr = [str(ltime[0]), str(ltime[1]).zfill(2), str(ltime[2]).zfill(2)]
timearr = [str(ltime[3] - 5).zfill(2), str(ltime[4]).zfill(2), str(ltime[5]).zfill(2)]
dtstr = "-".join(datearr) + "-" + "".join(timearr)
logfile = join(my_path,"logs","textbreaktest_{0}.log").format(dtstr)
print "logfile is: {0}".format(logfile)

# COMMENT OUT OPENING OF LOG FILE TO GET IMMEDIATE RESULTS IN TERMINAL
sys.stdout = open(logfile, 'w', encoding='utf-8')
print 'Log file for Testing Text Breaks ({0})'.format(dtstr)
print 'arguments: {0}'.format(args)

my_path = dirname(__file__)
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')
cat = Catalog.Catalog(catpath, 'Peltsek')

# Load vol ocr text names
volpath = join(my_path, '..', 'volsource')
vols = {}
vfiles = listdir(volpath)
for v in vfiles:
  match = search("\-vol(\d+)\_",v)
  if match:
    vols[match.group(1)] = v

if args.has_key('vol'):
  vkey = str(args['vol']).zfill(2)

txtct = 0
badtxt = 0
lnnotfound = 0

for vn in range(1,50):
  vkey = str(vn).zfill(2)
  if vols.has_key(vkey):
    print "Volume", vols[vkey]
    vol =  OCRVolume.Vol(join(volpath, vols[vkey]), int(vkey))
    vtoc = cat.getVolumeTOC(int(vkey), 'texts')
    # Iterate through texts in volume
    for t in vtoc:
      stpg = t.startpage
      txtct += 1
      # if it has a start page with a "." in it
      if stpg is not None and '.' in stpg:
        spp = t.startpage.split('.')
        stline = vol.getLine(spp[0],spp[1])
        
        if stline:
          found = searchForBreak(stline)
          
        else:
          newpg = int(spp[0]) + 1
          stline = vol.getLine(newpg,1)
          if stline:
            found = searchForBreak(stline)
          else:
            print "Cannot find line: {0}.{1}".format(spp[0],spp[1])
            lnnotfound += 1
        
        if found == 0:
          print t.key, "(" + stpg + ") ", " no delim found:"
          print stline
          badtxt += 1
          
      # if it has a start page but no "." 
      elif stpg is not None and stpg != "":
        stline = vol.getLine(stline, 1)
        if stline:
          found = searchForBreak(stline)
        if found == 0:
          print t.key, "(" + stpg + ") ", " assuming line 1, no delim found!"
          print stline
          badtxt += 1
      else:
        print "No line number"
        lnnotfound += 1
  

print "Total Texts: {0}".format(txtct)
print "Bad St lines: {0}".format(badtxt)
print "Lines not found or no number: {0}".format(lnnotfound)
for k in textdelims.keys():
  print k, "=>", textdelims[k]


