# coding=utf-8

#   A script to add refs to a digital texts bibl in the DTD declaration
#   Modifies the files in the given SVN repo folder "texts"

from os import listdir, remove, rename
from os.path import dirname, join
from OCRXml import *
import sys
from codecs import open

args= {}

for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

text_dir = "D:\\THL\\Repos\\1_development\\texts\\catalogs\\xml\\ngb\\pt\\texts"
for tdir in listdir(text_dir):
  for t in listdir(join(text_dir,tdir)):
    tpts = t.split("-text")
    tnm = tpts[0]
    infile = join(text_dir,tdir,t)
    outfile = infile.replace(".xml","-temp.xml")
    fin = open(infile, 'r', encoding='utf-8')
    fout = open(outfile, 'w', encoding='utf-8')
    for ln in fin:
      outstr = ln
      if '<!DOCTYPE TEI.2' in ln:
        outstr = '<!DOCTYPE TEI.2 SYSTEM "../../../../../../xml/dtds/xtib3.dtd" [ ' + "\n"
        outstr += '<!ENTITY ' + tnm + '-bib SYSTEM "../../0/' + tnm + '-bib.xml">' + "\n"
        outstr += "]>\n"
      elif '<sourceDesc' in ln:
        outstr = '<sourceDesc n="tibbibl">&' + tnm + '-bib;</sourceDesc>' + "\n"
      fout.write(outstr)
    fin.close()
    fout.close()
    remove(infile)
    rename(outfile, infile)


## Write vol bibs
#cat.write(join("out", "vols"), "volbibs")

#fout = open(outpath, 'w', encoding='utf-8')

  #fout.write(cat.tibToWylie(t.title) + "\n")
#  ln = t.key + "," + t.startpage + "," + t.endpage + "\n"
  
#fout.close()