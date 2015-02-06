# coding=utf-8

###################  convertVolToSimple.py ###########################
#
#   Converts given volume number from OCR markup to simple markup including text breaks
#
#    Usage:
#         python convertVolToSimple.py vol={####}
#     
#           All params option:
#               vol = simple volume number
#
###############################################################

import sys, time, re, codecs
from os.path import dirname, join
from os import listdir
from lxml import etree
from OCRXml import Catalog, OCRVolume, Text, Functions


##### MAIN #######
# Split args into a hash

args= {}
for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

if not args.has_key("vol"):
  print "Usage: \n\tpython convertVolToSimple.py vol={####}\n\n\tAll params option:\n\n\tvol = simple volume number"
  sys.exit()
else: 
  print "Volume number given is {0}".format(args["vol"].zfill(2))
  
my_path = dirname(__file__)

# Get Catalog
catpath = join(my_path, 'data', 'catalog', 'peltsek-with-lines.xml')
cat = Catalog.Catalog(catpath, 'Peltsek')

# Find the Volume OCR File
vnum = args["vol"].zfill(2) # Vol number to look for
volpath = join(my_path, 'data', 'volsource') # Volume OCR Path
vfiles = listdir(volpath) # List of all OCR Files
vf = [vf for vf in vfiles if re.search('nying-gyud-vol{0}_'.format(vnum), vf)][0]  # Find file in list

vol = OCRVolume.Vol(join(volpath, vf), vnum) # Open Volume file

voutpath = join(my_path, 'out', 'vols', 'ngb-pt-v{0}.xml'.format(vnum.zfill(3)))

vout = codecs.open(voutpath, 'w', encoding='utf-8')

vtoc = cat.get_volume_toc(vnum, "list")
lastStart = ""
lastLine = ""
for t in vtoc:
  print t["tnum"], t["start"], t["end"]
  t["range"] = vol.getRange(t["start"], t["end"], "div")
  
for n in range(0,len(vtoc)):
  tnum = vtoc[n]["tnum"].zfill(4)
  tstart = vtoc[n]["start"]
  tend = vtoc[n]["end"]
  print "Doing text {0}: {1} - {2}".format(tnum, tstart, tend)
  
  # if first text in vol or tstart of this text is not the same line as end of last text.
  print "start of text: {0}; end of previous text: {1}".format(tstart, vtoc[n - 1]["end"])
  if n == 0 or tstart != vtoc[n - 1]["end"]:
    if n != 0:
      vout.write("\n[ngb-pt-{0}:end]".format(tnum.zfill(4)))
    vout.write("\n[ngb-pt-{0}:start]".format(tnum))
    
    for pn in range(int(float(tstart)), int(float(tend)) + 1):
      stln = int(tstart[-1]) if pn == int(float(tstart)) else 1
      endln = int(tend[-1]) if pn == int(float(tend)) else 7
      if pn == int(float(tstart)) :
        print "Text Stln: {0}".format(stln)
      if pn == int(float(tend)):
        print "Text Endln: {0}".format(endln)
      if stln == 1:
        vout.write("\n[{0}]".format(pn))
        
      for ln in range(stln, endln):
        tln =  vol.getLine(pn, ln)
        if tln:
          vout.write("\n[{0}.{1}]".format(pn,ln) + tln)
    
  else: # if present text starts on the same line that last text ended on
    sppts = tstart.split('.')
    tbreak = vol.findTextBreak(sppts[0], sppts[1])
    print "text break found on {0}: 1 len: {1}, 2 len: {2}".format(tstart, len(sppts[0]), len(sppts[1]))
    vout.write("\n[{0}.{1}]".format(sppts[0], sppts[1]) + tbreak[0])
    ptnum = str(int(tnum) - 1).zfill(4)
    vout.write("\n[ngb-pt-{0}:end]".format(ptnum))
    vout.write("\n[ngb-pt-{0}:start]".format(tnum))
    if tstart[-1] == '6':
      print "Tstart: {0}".format(tstart)
      tstart = str(int(float(tstart)) + 1) + ".1"
    else:
      tstart = str((float(tstart) + .1))
    for pn in range(int(float(tstart)), int(float(tend)) + 1):
      stln = int(tstart[-1]) if pn == int(float(tstart)) else 1
      endrange = int(tend[-1]) if pn == int(float(tend)) else 7

      if stln == 1:
        vout.write("\n[{0}]".format(pn))
        
      for ln in range(stln, endrange):
        tln = vol.getLine(pn, ln)
        if tln:
          vout.write("\n[{0}.{1}]".format(pn,ln) + vol.getLine(pn, ln))

vout.close()

#print "catalog has {0} volumes!".format(len(cat.vols))
#print vol.tree
print "Volume {0} has {1} pages!".format(args["vol"], vol.totalPages())

print "Bye!"