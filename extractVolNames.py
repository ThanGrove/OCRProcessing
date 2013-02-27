# coding=utf-8

#   A script to read original peltsek vol files and extract volume information
#    into a single XML doc
#
#   Used to create ngb-pt-vols.xml file
#

import os
import codecs
import urllib
from lxml import etree

def tibToWylie(txt):
  url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
  q = {'conversion':'uni2wy', 'plain':'true', 'input' : unicode(txt).encode('utf-8') }
  out = ''
  fh = urllib.urlopen(url + urllib.urlencode(q))
  for l in fh.readlines():
    out += l
  fh.close()
  return out

volfolder = 'D:\\THL\\Cataloging\\Collections\\NGB\\Peltsek\\CatalogDocs\\Conversion\\vols\\1\\'
outfile = 'D:\\THL\\Programming\\Python\\ngbprocessing\\data\\ngb-pt-vols.xml'
outroot = etree.Element('vollist')
svnum = 0
for v in os.listdir(volfolder):
  # Get volume file and parse XML
  vf = volfolder + v
  vtree = etree.parse(vf)
  vroot = vtree.getroot()
  
  # Calculate sequential id
  svnum += 1
  vid = "ngb-pt-v{0}".format(str(svnum).zfill(2))
  
  # vol id and number
  vel = etree.Element("volume", id=vid)
  vnumel = etree.Element("num")
  vnum = vroot.get('n')
  vnumel.text = vnum
  vel.append(vnumel)
  print "Processing volume {0} ({1})".format(str(svnum), vnum)
  # Deal with name
  vnametibel = etree.Element("name", lang="tib")
  vnamewyel = etree.Element("name", lang="wylie")
  els = vroot.xpath('/*//name[1]')
  if len(els) > 0:
    tibnm = els[0].text
    vnametibel.text = tibnm
    wynm = tibToWylie(tibnm)
    vnamewyel.text = wynm
  vel.append(vnametibel)
  vel.append(vnamewyel)
  
  # Deal with dox
  vdox = etree.Element("dox")
  els = vroot.xpath('/*//doxography[1]')
  if len(els) > 0:
    doxval = els[0].text
    vdox.text = doxval
  vel.append(vdox)
  
  # Number of texts
  els = vroot.xpath('/*//text')
  tnumel = etree.Element("textcount")
  tnumel.text = str(len(els))
  vel.append(tnumel)
  
  # Add vol element to root
  outroot.append(vel)
  
# Output resulting XML doc
fout = codecs.open(outfile, 'w', encoding='utf-8')
fout.write(etree.tostring(outroot, pretty_print=True, encoding=unicode))
fout.close()
  
  


