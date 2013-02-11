# coding=utf-8
import urllib

# idel, text, vnum, and tnum elements: variables that holds the name of the those respective tags
idel = "key"                 # name of element that holds the sequential text number (or ID)
textelement = "textrecord"   # element that holds a texts data
vnumelement = "vnum"         # element with the volume number
mytnumel = "tnum"            # element with the text number (sequentiall from the beginning)
# textprops: a list of all property names (= child elements) of a text record
textprops = ["tnum", "key", "title", "vnum", "startpage", "endpage", "numofchaps", "chaptype", "doxography", "translators", "crossrefs", "notes"]

def tibToWylie(txt):
  url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
  q = {'conversion':'uni2wy', 'plain':'true', 'input' : unicode(txt).encode('utf-8') }
  out = ''
  fh = urllib.urlopen(url + urllib.urlencode(q))
  for l in fh.readlines():
    out += l
  fh.close()
  return out