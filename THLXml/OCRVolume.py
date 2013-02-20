# coding=utf-8

import re
from lxml import etree
from copy import deepcopy
from . import Vars

def is_number(s):
  try:
      float(s)
      return True
  except ValueError:
      return False
    
##### OCRVol Class #####
class Vol():
  docpath = ""
  tree = None
  number = ""
  # txtdelims:
  # 1: rgya gar skad du, 2:  gar skad du/, 3: rdzogs so//, 4: phyag tshal
  txtdelims = [u'རྒྱ་གར་སྐད་དུ', u'གར་སྐད་དུ།']  
  
  def __init__(self, path, number):
      """Takes a path to an XML document and parses it, reading in a volume's ocr document"""
      try:
        self.number = number
        self.tree = etree.parse(path)
        
        # find missing milestones and if lines after are -1.1 then it is not really missing
        # Adjust the page number to be between the previous and following one if that number is missing
        # Or else no change
        for m in self.tree.xpath('/*//milestone[@unit="missing"]'):
          nval = m.get("n")
          pel = m.getprevious()
          nel = m.getnext()
          natn = nel.get("n").split('.')[0]
          while nel is not None and natn == "-1":
            nel = nel.getnext()
            if nel is not None:
              natn = nel.get("n").split('.')[0]
          nextm = m.getnext()
          match = re.search('_(\d+)\.tif', nval)
          if match and pel is not None and nextm is not None:
            pnum = int(match.group(1))
            pnval = pel.get('n').split('.')[0]
            nnval = nextm.get('n').split('.')[0]
            
            nmatch = re.search('out_(\d+)', natn)
            
            if nmatch:
              natn = int(nmatch.group(1))
              
            if is_number(pnval) and is_number(natn) and int(natn) - int(pnval) == 2:
              pnum = int(pnval) + 1
              
            if nextm is not None and nextm.get("unit") == "line":
              m.set("unit","page")
              m.set("n", str(pnum))
              nnval = nextm.get("n").split(".")
              while nnval[0] == "-1":
                nnval[0] = str(pnum)
                nextm.set("n", ".".join(nnval))
                
                if nextm is not None:
                  nextm = nextm.getnext()
                  
                if nextm is None or nextm.get("unit") != "line":
                  break
                
                else:
                  nnval = nextm.get('n').split('.')
                
            #print "this: {0}, next: {1}".format(str(pnum), nextm.get("unit"))
          #else:
            #print "Missing page: {0}".format(nval)
        
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
    if isinstance(tx, XMLText.TextCat):
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
    #else:
    #  print "Unable to find page {0} in volume {1}".format(pn, self.number)
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
    if "." not in st:
      st = st + ".1"
    if "." not in en:
      en = en + ".6"
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
    
    if not query and pn == 1:
      pn = 2
      xp = xp = '/*//milestone[@unit="' + unit + '" and @n="' + str(pn) + '"]' # Xpath to find page milestone with nvalue = pn
      query = t.xpath(xp)
      
    if query:
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
        
    else:
      print "XPath Failed for Vol {0}".format(self.number)
      print "\t{0}".format(xp)
      
    return rng
  
  def findMilestones(self, pg): 
    for m in self.tree.xpath('/*//milestone[@n="' + pg + '"]'):
      print m.get("unit"), m.get("n")
      nxtm = m.getnext()
      while nxtm is not None and pg in nxtm.get("n"):
        print nxtm.get("unit"), nxtm.get("n")
        nxtm = nxtm.getnext()
    
  def textStartLine(self, n):
    pg = self.getPage(n)
    for m in pg.iter('milestone'):
      if m.get('unit') == "line":
        sl = re.search('\.(\d+)', m.get('n'))
        if sl:
          foundInLine = self.testLine(m)
          if foundInLine == True:
            return sl.group(1)
    return False
    
  def testLine(self, m):
    for tss in self.txtdelims:
      mt = m.tail
      if mt.find(tss) > -1:
        #print XMLVars.tibToWylie(tss),":", XMLVars.tibToWylie(mt)
        return True
    return False
            
  def textStartsAtTop(self, n):
    sl = self.textStartLine(n)
    if sl == "1":
      line = self.getLine(n,1)
      ln = len(line)
      for tss in self.txtdelims:
        pos = line.find(tss)
        if pos < ln:
          ln = pos
      if ln < 10:
        return True
    return False
  
##### End of OCRVol Class ####