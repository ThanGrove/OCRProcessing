# coding=utf-8

import re
from lxml import etree
from copy import deepcopy
from . import XMLVars, XMLText

##### OCRVol Class #####
class Vol():
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