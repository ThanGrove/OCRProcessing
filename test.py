# coding=utf-8

#   A script to read in catalog data, check the OCR volumes for the line the text begins and ends on
#     update and write out the data again.

from os.path import dirname, join
from THLXml import *
import sys

args= {}

for a in sys.argv:
  if sys.argv.index(a) > 0:
    if "=" in a:
      pts = a.split("=")
      args[pts[0]] = pts[1]
    else:
      args[sys.argv.index(a)] = a

my_path = dirname(__file__)
catpath = join(my_path, 'data', 'peltsek-with-lines.xml')

# example of vol 1.
volpath = join(my_path, '..', 'volsource', 'nying-gyud-vol01_than_gDR0Y3578hI0.txt')

vol =  OCRVolume.Vol(volpath, 1)


vol.findMilestones("44")
vol.findMilestones("45")
vol.findMilestones("46")

