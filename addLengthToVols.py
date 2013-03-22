# coding=utf-8

#   A script add number of pages to the vol info

import os
from os.path import dirname, join
from lxml import etree
from THLXml import *
import sys
from codecs import open

my_path = dirname(__file__)
dt = Functions.getDateTime()
volinfopath = join(my_path, 'data', 'ngb-pt-vols.xml')
volinfo = etree.parse(volinfopath)
volinfodoc = volinfo.getroot()
outvolpath = join(my_path, 'data', 'ngb-pt-vols_{0}.xml'.format(dt))
volsrcpath = join(my_path, '..', 'volsource')

for vfile in os.listdir(volsrcpath):
  vpath = join(volsrcpath, vfile)
  vol = OCRVolume.Vol(vpath)
  vid = "ngb-pt-v" + vol.number
  mss = vol.tree.xpath("/*//milestone[@unit='page']")
  nind = -1
  n = mss[nind].get("n")
  while int(n) < 100 and nind > -10:
    nind = nind - 1
    n = mss[nind].get("n")
  if len(mss) - 100 > int(n):
    n = len(mss)
  #print vol.number + "," + vpath + "," + str(len(mss)) + "," + n
  vel = volinfodoc.find("volume[@id='" + vid + "']")
  pgel = etree.Element("pages")
  pgel.text = str(n)
  vel.append(pgel)

print "Writing new vol info file: {0}".format(outvolpath)
volinfo.write(outvolpath, encoding='utf-8')
#fout = codecs.open(outvolpath, 'w', encoding='utf-8')
#fout.write(etree.tostring(volinfodoc, encoding=unicode))
#fout.close()


