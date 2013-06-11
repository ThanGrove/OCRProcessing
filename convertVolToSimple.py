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
from os import listdir, remove
from lxml import etree
from THLXml import Catalog, OCRVolume, Text, Functions


def findTextBreak(ln, btxt):
  # txtdelims:
  txtdelims = [u'།*\s*རྒྱ་གར་སྐད་དུ', u'།*\s*བོད་སྐད་དུ', u'རྫོགས་སོ།།']  
  print "break text is: {0}\n".format(btxt)
  for td in txtdelims:
    match = re.search(td,ln)
    if match:
      print "found a break\n"
      td = match.group(0)
      lpts = ln.split(td)
      if td == txtdelims[-1]:
        ln = lpts[0] + td + btxt + lpts[1]
      else: 
        ln =  lpts[0] + btxt + td + lpts[1]
      break
  return ln if match else (btxt + ln)

#### END OF findTextBreak
  
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

print "path is: {0}".format(join(volpath, vf))
vol = OCRVolume.Vol(join(volpath, vf), vnum) # Open Volume file

voutpath = join(my_path, 'out', 'vols', 'ngb-pt-v{0}-tmp.xml'.format(vnum.zfill(3)))

vout = codecs.open(voutpath, 'w', encoding='utf-8')

vtoc = cat.getVolumeTOC(vnum, "list")
vstart = vtoc[0]["start"]
vstln = vstart[-1]
vstart = float(vstart)
vend = vtoc[-1]["end"]
vendln = vend[-1]
vend = float(vend)
volinfo = cat.getVolume(vnum)

print "Doing volume {0}, pages {1} to {2}".format(vnum, vstart, vend)
n = 0

vout.write("<!-- Volume TOC: \n")
for v in vtoc:
  vout.write("Text {0}: {1} - {2}\n".format(v['tnum'].zfill(4), v['start'], v['end']))
vout.write(" -->\n")

isstart = 0
vout.write('[ngb-pt-{0}:start]'.format(vtoc[0]["tnum"].zfill(4)))
for pn in range(int(vstart),int(vend) + 1):
  print "Doing page {0}".format(pn)
  vout.write('[{0}]'.format(pn) + "\n")
  for ln in range(1,7):
    lntxt = vol.getLine(pn, ln)
    if lntxt:
      #print "{0}, {1}, {2}, {3}".format(n, len(vtoc), vtoc[n]["start"], str(pn) + "." + str(ln))
      if n < len(vtoc) and vtoc[n]["start"] == str(pn) + "." + str(ln):
        print "here"
        breaktxt = "[ngb-pt-{0}:end]\n[ngb-pt-{1}:start]".format(vtoc[n - 1]["tnum"].zfill(4), vtoc[n]["tnum"].zfill(4))
        lntxt = findTextBreak(lntxt, breaktxt)
        n += 1
      elif n < len(vtoc) and float(vtoc[n]["start"]) < float(str(pn) + "." + str(ln)):
        n += 1
      vout.write('[{0}.{1}]'.format(pn,ln) + lntxt  + "\n")
vout.write('[ngb-pt-{0}:end]'.format(vtoc[-1]['tnum']))  
vout.close()

print "Cleaning up out file!"
voutpathfinal = voutpath.replace('-tmp','')

vout = codecs.open(voutpath, 'r', encoding="utf-8")
vin = vout.read()
vout.close()
vin2 = re.sub(r'\s*(\[\d+\]\s*\[\d+\.\d\])\s*(\[ngb-pt-\d+\:end\])\s*(\[ngb-pt-\d+\:start\])', r'\n\2\n\3\n\1\n', vin)

vout = codecs.open(voutpathfinal, 'w', encoding="utf-8")
vout.write(vin2)
vout.close()
remove(voutpath)
print "Done! Bye!"