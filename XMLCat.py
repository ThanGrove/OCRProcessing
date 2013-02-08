# coding=utf-8
import os
import sys
import codecs
import urllib
import re
from lxml import etree
from copy import deepcopy

sep = os.sep

# XMLCommonVars is a super class which has only the variables that both XMLCat and XMLText inherit
class XMLCommonVars:
  # text, vnum, and tnum elements: variables that holds the name of the those respective tags
  textelement = "textrecord"   # element that holds a texts data
  vnumelement = "vnum"         # element with the volume number
  mytnumel = "tnum"            # element with the text number (sequentiall from the beginning)
  # textprops: a list of all property names (= child elements) of a text record
  textprops = ["tnum", "key", "title", "vnum", "startpage", "endpage", "numofchaps", "chaptype", "doxography", "translators", "crossrefs", "notes"]


#### XMLCat Class   ####
class XMLCat(XMLCommonVars):
  """A class for processing an XML document that is a list of texts.
     The XML expected here is based on the simple schema for mapping from an Excell document, Peltsek_Excell_Datamap.xsd
     This is a <spreadsheet> element with a series of <textrecord>s in it. Each text record has the following children:
       tnum, key, title, vnum, startpage, endpage, numofchaps, chaptype, doxography, translators, crossrefs, notes """
  docpath = ""
  tree = None
  name = ""
  vols = {}
  texts = {}
  
  def __init__(self, path, name):
    """Takes a path to an XML document and parse it, creating two dictionary attributes: 
        1. vols = an dictionary of volumes keyed on vol num and 2. texts a dictionary of texts keyed on text num"""
    try:
      self.name = name
      self.tree = etree.parse(path)
      root = self.tree.getroot()
      rows = root.xpath('/*//' + self.textelement)
      seqvnum = 0
      oldvnum = 0
      for r in rows:
        vnum = r.find(self.vnumelement).text  # volume number in catalog
        if vnum != oldvnum:                    # sequential volume number
          seqvnum += 1
          oldvnum = vnum
        pt = r.itersiblings(tag=self.textelement, preceding=True) 
        tnum = len(list(pt)) + 1 # calculate text number as number of preceding siblings plus one
        if seqvnum in self.vols:
          self.vols[seqvnum].append(tnum)
        else:
          self.vols[seqvnum] = [tnum]
        se = etree.SubElement(r, "key")
        se.text = unicode(str(tnum))
        self.texts[tnum] = r
      self.textcount = len(self.texts)
      self.volcount = len(self.vols)
    except IOError:
      print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(path)

  def getVolume(self, n):
    """Returns a text object"""
    if self.vols.has_key(n):
      return self.vols[n]
    else:
      return None
    
  def getText(self, n):
    """Returns a text object"""
    if self.texts.has_key(n):
      return XMLText(self.texts[n])
    else:
      return None
  
  def getVolumeTOC(self, n, method='plain'):
    voltoc = []
    if self.vols.has_key(n):
      for tn in self.getVolume(n):
        txt = self.getText(tn)
        if method == 'list':
          voltoc.append({"key":txt.key, "tnum":txt.tnum, "title":txt.title, "vnum":txt.vnum, "start":txt.startpage, "end":txt.endpage})
        else:
          title = tibToWylie(txt.title)
          print txt.key, txt.tnum, wytitle, txt.vnum, txt.startpage, txt.endpage
    else:
      print "There is no volume {0}".format(n)
    if method == 'list':
      return voltoc
      
  def iterTexts(self):
    txts = self.texts
    for k, txt in txts.iteritems():
      yield XMLText(txt)
      
#### End of XMLCat Class ###

####  XMLText Class ####
class XMLText(object, XMLCommonVars):
  """XML Text: An Object for manipulating XML data about one text in a catalog"""
  
  # Not necessary to define properties here but help tips in IDEs use them if explicit
  tnum = ""  # the given text number from the record in the catalog not necessarily sequential
  key = ""   # absolutely sequential text number and the key for the text in the texts dictionary of the XMLCat
  title = "" 
  vnum = "" 
  startpage = "" 
  endpage = "" 
  numofchaps = "" 
  chaptype = "" 
  doxography = "" 
  translators = "" 
  crossrefs = "" 
  notes = ""
  
  def __init__(self, t):
    for p in self.textprops:
      setattr(self, p, t.find(p).text)
  
  def __type__(self):
    return "XMLText"
  
  def JSON(self):
    """Returns a unicode JSON object of the text's attributes""" 
    out = u'{"' # Open JSON object
    kvsep = u'":"'  # Separator between key and value
    itemsep = u'", "' # Separator between items
    for p in self.textprops: # loop through attributes from props list
      out += p + kvsep
      val = getattr(self,p) # Get attribute value
      # Account for NoneTypes or null attributes
      if val == None:
        out += u""
      else:
        out += val
      out += itemsep
    out = out[:-3] + u'}' # remove last 3 character (, ") and close JSON object
    return out  # return value is unicode
      
#### End of XMLText Class ###   


##### OCRVol Class #####
class OCRVol():
  docpath = ""
  tree = None
  number = ""
  # txtdelims:
  # 1: rgya gar skad du, 2:  gar skad du/, 3: rdzogs so//, 4: phyag tshal
  txtdelims = [u'རྒྱ་གར་སྐད་ད', u'གར་སྐད་དུ།', u'རྫོགས་སོ།།', u'ཕྱག་ཚལ']  
  
  def __init__(self, path, number):
      """Takes a path to an XML document and parses it, reading in a volume's ocr document"""
      try:
        self.number = number
        self.tree = etree.parse(path)
      except IOError:
        print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(path)
        
  def totalPages(self):
    return int(self.tree.xpath('count(/*//milestone[@unit="page"])'))
  
  def hasPage(self, pn):
    t = self.tree                 # cataloge tree = t
    # Finde the milestone
    xp = '/*//milestone[@unit="page" and @n="' + str(pn) + '"]' # Xpath to find page milestone with nvalue = pn
    query = t.xpath(xp)
    return True if len(query) == 1 else False
    
  def getPage(self, pn, tx=None):
    """Returns a stand-alone XML document with root <xpage> containing the page of text desired along with milestones"""
    # Could add option to not include milestones and also one just to return plain text
    page = etree.Element('xpage') # make a new xpage element to return
    if isinstance(tx, XMLText):
      page.set('tnum', tx.key)
    t = self.tree                 # cataloge tree = t
    # Finde the milestone
    xp = '/*//milestone[@unit="page" and @n="' + str(pn) + '"]' # Xpath to find page milestone with nvalue = pn
    query = t.xpath(xp)
    if len(query) > 0:
      # Copy it and append to xpage output element
      cp = deepcopy(query[0])
      if type(query[0].tail) == 'str':
        cp.tail = query[0].tail # add the text following the milestone if any (shouldn't be)
      page.append(cp)
      
      # Iterate its siblings until a new page milestone is met and add to output xpage element
      #    page milestone siblings will be line milestones
      for sib in query[0].itersiblings():
        if sib.get('unit') == 'page':
          break;
        cp = deepcopy(sib)         # Copy the line milestone
        if type(sib.tail) == 'str':
          cp.tail = query[0].tail  #  Add the text after the line milestone also
        page.append(cp)  #  append the whole thing to the output element
    else:
      print "Unable to find page {0} in volume {1}".format(pn, self.number)
    return page    # return the <xpage> element with the text and milestones for that page
      
  def getLine(self, pn, ln):
    """Returns just a line of text without any milestone"""
    t = self.tree
    xp = '/*//milestone[@unit="line" and @n="' + str(pn) + '.' + str(ln) + '"]' # Xpath to find page milestone with nvalue
    query = t.xpath(xp)
    # Use regex to eliminate multiple whitespaces and line returns
    return re.sub(re.compile(r'\s+'), ' ', query[0].tail) if len(query) > 0 else False
  
  def getRange(self, st, en, el="div1"):
    """Get a range of text in the volume and return in the element of ones choice"""
    stpg = st.split('.')
    t = self.tree               # The vol xml file
    rng = etree.Element(el)     # Start the output element "rng"
    rng.set('st', st)
    rng.set('en', en)
    unit = 'line'
    pn = st
    if stpg[1] == '1':
      unit = 'page'
      pn = stpg[0]
    xp = xp = '/*//milestone[@unit="' + unit + '" and @n="' + str(pn) + '"]' # Xpath to find page milestone with nvalue = pn
    query = t.xpath(xp)
    # Copy it and append to xpage output element
    cp = deepcopy(query[0])
    if type(query[0].tail) == 'str':
      cp.tail = query[0].tail # add the text following the milestone if any (shouldn't be)
    rng.append(cp)
    
    # Iterate its siblings until a line milestone with n greater than en variable
    #    is met and add to output rng element
    #    page milestone siblings will be line milestones
    for sib in query[0].itersiblings():
      try:
        if float(sib.get('n')) > float(en):
          break;
      except ValueError:
        nval = sib.get('n')
        print "None numeric n value: {0}".format(nval)
      cp = deepcopy(sib)         # Copy the line milestone
      if type(sib.tail) == 'str':
        cp.tail = query[0].tail  #  Add the text after the line milestone also
      rng.append(cp)  #  append the whole thing to the output element
    return rng
  
  def textStartLine(self, n):
    pg = self.getPage(n)
    mxln = 0
    for textstartstr in self.txtdelims:
      for m in pg.iter('milestone'):
        if m.get('unit') == "line":
          mt = m.tail
          if mt.find(textstartstr) > -1:
            sl = re.search('\.(\d+)', m.get('n'))
            if sl:
              return sl.group(1)
    return False
    
  def textStartsAtTop(self, n):
    sl = self.textStartLine(n)
    return True if sl and sl == 1 else False
  
##### End of OCRVol Class ####

#### Stand-Alone Functions ####
def printEndPagesForVol(cat, vpath, vnum, fnm):
  fout = codecs.open(fnm, 'w', encoding='utf-8')
  fout.write('<?xml version="1.0" encoding="UTF-8"?><endpages v="3">')
  vol = OCRVol(vpath, vnum)
  for t in cat.iterTexts():
    if t.vnum == str(vnum):
      pn = t.endpage
      if vol.hasPage(pn):
        pg = vol.getPage(pn, t)
        fout.write(etree.tostring(pg, pretty_print=True, encoding=unicode))
  fout.write('</endpages>')
 
def findTextEndLines(cat, vpath, vnum, fnm):
  vol = OCRVol(vpath, vnum)
  for t in cat.iterTexts():
    if t.vnum == str(vnum):
      pn = t.endpage
      if vol.hasPage(pn):
        pg = vol.getPage(pn, t)
        print type(pg)
  
def tibToWylie(txt):
  url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
  q = {'conversion':'uni2wy', 'plain':'true', 'input' : unicode(txt).encode('utf-8') }
  out = ''
  fh = urllib.urlopen(url + urllib.urlencode(q))
  for l in fh.readlines():
    out += l
  fh.close()
  return out
  
def createTextsFromVol(cat, volfilepath, vnum):
  vol = OCRVol(volfilepath, vnum)
  # Iterate through text numbers in vol 3 and output texts
  for tn in cat.getVolume(vnum):
    t = cat.getText(tn)
    print str(tn) + ": " + tibToWylie(t.title)
    fnm = foutname + "ngb-pt-{0}.xml".format(tn)
    fout = codecs.open(fnm, 'w', encoding='utf-8')
    if vol.textStartsAtTop(t.endpage):
      t.endpage = str(int(t.endpage) - 1)
    txtrg = vol.getRange(t.startpage + '.1', t.endpage + '.6')
    fout.write(etree.tostring(txtrg, encoding=unicode))
    fout.close()
    
def processNGBVolumes(cat, volpath):
  print "volpath: {0}".format(volpath)
  dirlist = os.listdir(volpath)
  for f in dirlist:
    m = re.search('\-vol(\d+)\_', f)
    vnum = int(m.group(1))
    outvolbreaksfile = '..{0}output{0}textbreaks{0}ngb_v'.format(sep) + m.group(1) + '_textbreaks.xml'
    #print "Text breaks for vol {0}: {1}".format(vnum, outvolbreaksfile)
    #printEndPagesForVol(cat, volpath + f, vnum, outvolbreaksfile)
    #createTextsFromVol(cat, volpath + f, vnum)
    findTextEndLines(cat, volpath + f, vnum, outvolbreaksfile)
    break
    
def test():
  print "hey"
  print os.getcwd()
  print sep
  
######### MAIN ROUTINE ##########
#  Putting in its own function so it appears in editor toc

def main():
  # Get commandline parameters
  datafolder = '..{0}data{0}'.format(sep)
  catpath = datafolder + 'peltsek.xml'
  volfolder = '..{0}source{0}'.format(sep)
  volpath =  volfolder + 'nying-gyud-vol02_than_KD5jc1bUVeUZ.txt'
  
  # Open test out file and run test commands
  foutname = '..{0}output{0}'.format(sep)
  
  
  # Instantiate the Peltsek Catalog
  cat = XMLCat(catpath, 'Peltsek')
  #print "calling processNGBVolumes()"
  #processNGBVolumes(cat, volfolder)
  #test()
  #createTextsFromVol(cat, fvolpath + volname, 3)
  
  # Instantiate volume 3
  for f in os.listdir(volfolder):
    m = re.search('\-vol(\d+)\_', f)
    vnum = int(m.group(1))
    volpath = volfolder + f
    vol = OCRVol(volpath, vnum)
    vtxtlist = cat.getVolumeTOC(vnum, 'list')
    for t in vtxtlist:
      mystpg = t['start']
      print "{0}:{1}:{2}".format(t['key'], mystpg, vol.textStartLine(mystpg))
  
  #print vol.textStartsAtTop(114)
  
  
  #printEndPagesForVol(cat, 3, fvolpath + volname, fout)
  
  #t3 = cat.getText(28)
  #txtrg = vol.getRange(t3.startpage + '.1', t3.endpage + '.6')
  #fout = codecs.open(foutname, 'w', encoding='utf-8')
  #fout.write(etree.tostring(txtrg, encoding=unicode))
  #fout.close()
  #print "Text {0} written to file.".format(t3.key)
  #print tibToWylie(t3.title)  ## vol.getLine(141, 5)
  
  
  #cat.getVolumeTOC(3)

######## End of Main Routine ########

## Call  Main
if __name__ == "__main__":
  main();

