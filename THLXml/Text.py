# coding=utf-8

from lxml import etree
from . import Vars, OCRVolume
from os.path import dirname, join
from re import search
from codecs import open
from urllib import urlopen, urlencode
from copy import deepcopy
import time
import datetime

def tibToWylie(txt):
  url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
  q = {'conversion':'uni2wy', 'plain':'true', 'input' : unicode(txt).encode('utf-8') }
  out = ''
  fh = urlopen(url + urlencode(q))
  for l in fh.readlines():
    out += l
  fh.close()
  return out

def findTransBreak(txt):
  insp = [u'གིས་', u'གྱིས་', u'ཀྱིས་', u'ཡིས་', u'པས་བསྒྱུར།', u'བས་བསྒྱུར།', u'ས་བསྒྱུར།']  # Intrumental particles for translator interpretation
  for isp in insp:
    if isp in txt:
      return isp
  return False

def splitTranslators(tstr):
  tbks = [u'དང་', u'། ']  # Strings to break up translators
  res = []
  for tbk in tbks:
    if tbk in tstr:
      res = tstr.split(tbk)
  if len(res) == 0:
    res.append(tstr)
  return res
  

my_path = dirname(__file__)
tmpl_path = join(my_path, 'templates')
data_path = join(my_path, '..', 'data')
today = str(datetime.date.today())

####  THLText Class ####
class Text(object):
  """THL Text: An Object for manipulating XML data about one text in a catalog"""
  
  # Catalog and Edition ID related properties 
  cat = None # parent catalog
  thlid = ""
  coll = ""
  ed = ""
  
  # Text Properties
  # Property names are read from THLXml.Vars file but are defined here to show in IDE
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
  
  def __init__(self, t, parent = None):
    if parent != None:
      self.cat = parent
    for p in Vars.textprops:
      setattr(self, p, t.find(p).text)
  
  def __type__(self):
    return "THL Text"
  
  def set(self, atnm, val):
    setattr(self, atnm, val)
    if atnm == "thlid":
      match = search(r'^([^\-]+)-([^\-]+)', val)
      if match:
        self.coll = match.group(1)
        self.ed = match.group(2)
      else:
        print "no match"
        
  def setParent(self, parent):
    if type(parent) == "instance" and parent.__type__() == "THL Catalog":
      self.cat = parent
      
  def toJSON(self, tibetan="unicode"):
    """Returns a unicode JSON object of the text's attributes""" 
    out = u'{"' # Open JSON object
    kvsep = u'":"'  # Separator between key and value
    itemsep = u'", "' # Separator between items
    for p in Vars.textprops: # loop through attributes from props list
      out += p + kvsep
      val = getattr(self,p) # Get attribute value
      if tibetan == "wylie":
        if p == "title" or p == "chaptype" or p == "doxography" or p == translators or p == "crossrefs" or p == "notes":
          val = tibToWylie(val)
      # Account for NoneTypes or null attributes
      if val == None:
        out += u""
      else:
        out += val
      out += itemsep
    out = out[:-3] + u'}' # remove last 3 character (, ") and close JSON object
    return out  # return value is unicode
  
  def getData(self, datatype="tuple", tibetan="unicode"):
    t = self
    if datatype == "json":
      return self.toJSON(tibetan)
    else:
      title = t.title
      chptype = t.chaptype
      dox = t.doxography
      trans = t.translators
      crefs = t.crossrefs
      notes = t.notes
      
      if tibetan == "wylie":
        title = tibToWylie(title)
        chptype = tibToWylie(chptype)
        dox = tibToWylie(dox)
        trans = tibToWylie(trans)
        crefs = tibToWylie(crefs)
        notes = tibToWylie(notes)
        
      # QUESTION! Are these t.tnum values etc stored as values or references to the object?
      if datatype == "array":
        return [t.key, t.tnum, title, t.vnum, t.startpage, t.endpage, t.numofchaps, chptype,
                    dox, trans, crefs, notes]
      
      elif datatype == "dictionary":  
        return { "key": t.key, "tnum": t.tnum, "title": title,
                    "vnum": t.vnum, "startpage": t.startpage, "endpage": t.endpage,
                    "numofchaps": t.numofchaps, "chaptype": chptype,
                    "doxography": dox, "translators": trans,
                    "crossrefs": crefs, "notes": notes }
      
      else:  # Default datatype is tuple 
        return (t.key, t.tnum, title, t.vnum, t.startpage, t.endpage, t.numofchaps, chptype,
                  dox, trans, crefs, notes)
    
  def writeTextBibl(self, path = None, name = None):
    if path == None:
      path = join(my_path, '..')
    if name == None:
      name = self.thlid + ".xml"
      
    # Read in the template tibbibl
    template = join(tmpl_path, 'tibbibl.xml')
    doc = etree.parse(template)
    txml = doc.getroot()
    
    txml.set('id',self.thlid)
    # Setting SYSID
    self.setTemplateVal(txml, "//sysid", self.thlid + ".xml")
    # Setting Today's Date
    self.setTemplateVal(txml, "//date[@n='today']", today)
    
    # Setting Title
    tle = self.title
    wytle = tibToWylie(tle)
    self.setTemplateVal(txml, "//title[@id='normtitle']", tle, wytle )
    self.setTemplateVal(txml, "//title[@id='title']", tle, wytle)
    
    # Setting Text ID
    self.setTemplateVal(txml, "//tibid[@id='tnum']", self.key)
    # Setting Volume information
    self.setTemplateVal(txml, "//tibid[@id='vnum']", self.vnum)
    vol = self.cat.getVolume(self.vnum)
    self.setTemplateVal(txml, "//altid[@id='altid']", vol['tib'], vol['wylie'])
    tinv = vol['texts'].index(int(self.key)) + 1
    self.setTemplateVal(txml, "//tibid[@id='tinv']", str(tinv))
    # Setting pagination
    if type(self.startpage) == "str":
      sp = self.startpage.split('.')
      self.setTemplateVal(txml, "//num[@id='spp']", sp[0])
      if len(sp) > 1:
        self.setTemplateVal(txml, "//num[@id='spl']", sp[1])
    
    if type(self.endpage) == "str":
      ep = self.endpage.split('.')
      self.setTemplateVal(txml, "//num[@id='epp']", ep[0])
      if len(ep) > 1:
        self.setTemplateVal(txml, "//num[@id='epl']", ep[1])
    if type(self.startpage) == "str" and type(self.endpage) == "str":
      tp = int(ep[0]) - int(sp[0]) + 1
      self.setTemplateVal(txml, "//extent[@id='tpps']", str(tp))
      
    # Setting Doxography
    dtib = self.doxography
    dwyl = []
    doxel = txml.xpath("//doxography[@id='doxcat']")[0]
    for dtib in dtib.split('::'):
      dwyl = tibToWylie(dtib)
      rs = etree.Element("rs")
      c = etree.Comment(dwyl)
      c.tail = dtib
      rs.append(c)
      doxel.append(rs)
    
    # Setting Translators
    trans = self.translators
    tdecl = txml.xpath("//respdecl[@type='translator']")[0]
    if tdecl is not None and trans is not None:
      tdecl.insert(0,etree.Comment(tibToWylie(trans) + " : " + trans))
      tbk = findTransBreak(trans)
      if tbk:
        trans = trans.split(tbk)[0]
      trans = splitTranslators(trans)
      if len(trans) > 0:
        self.setTemplateVal(txml, "//persName[@id='istrans']", trans[0], tibToWylie(trans[0]))
        if len(trans) > 1:
          transel = deepcopy(txml.xpath("//persName[@id='tttrans']")[0])
          transel.attrib.pop('id')
          self.setTemplateVal(txml, "//persName[@id='tttrans']", trans[1], tibToWylie(trans[1]))
          if len(trans) > 2:
            for n in range(2,len(trans)):
              tel = deepcopy(transel)
              c = etree.Comment(tibToWylie(trans[n]))
              c.tail = trans[n]
              tel.append(c)
              transel.append(tel)
      else:
        print "No translators found!"
    else:
      pn = txml.xpath("//persName[@id='istrans']")[0]
      pn.set("lang", "eng")
      pn.text = "Not specified."
      pn.attrib.pop("id")
      pn = txml.xpath("//persName[@id='tttrans']")[0]
      pn.set("lang", "eng")
      pn.text = "Not specified."
      pn.attrib.pop("id")
    
    # Writing out the XML Bibl record for the text
    fout = open(join(path, name), 'w', encoding='utf-8')
    fout.write(etree.tostring(doc, encoding=unicode))
    fout.close()
    
  def writeText(self, path = None, name = None):
    if path == None:
      path = join(my_path, '..')
    if name == None:
      name = self.thlid + ".xml"
      
    # Read in the template tibbibl
    template = join(tmpl_path, 'text.xml')
    doc = etree.parse(template)
    txml = doc.getroot()
    txml.set('id', self.thlid + ".xml")
    self.setTemplateVal(txml, "/*//title[@id='title']", self.title, tibToWylie(self.title))
    self.setTemplateVal(txml, "/*//idno[@id='thlid']", self.thlid)
    self.setTemplateVal(txml, "/*//date[@id='today']", today)
    vol = self.cat.getVolume(self.vnum)
    ocrvol = OCRVolume.Vol(vol['ocrfile'], self.vnum)
    
    # Get the actual text from OCR Volume and put in div1 of text template
    div1 = txml.xpath("/*//div1[@id='content']")[0]
    div1.attrib.pop("id")
    for child in div1:
      div1.remove(child)
    div1.append(ocrvol.getRange(self.startpage,self.endpage,'p'))
    
    # Writing out the XML Text file
    fout = open(join(path, name), 'w', encoding='utf-8')
    fout.write(etree.tostring(doc, encoding=unicode))
    fout.close()
    
  def setTemplateVal(self, doc, xp, val, cmt = ""):
    atnm = "id"
    match = search(r'\[\@(\w+)=', xp)
    if match:
      atnm = match.group(1)
    els = doc.xpath(xp)
    if len(els) == 0:
      print "Xpath: {0} not found".format(xp)
    else:
      el = els[0]
      for sel in el:
        list(el).pop()
      if cmt != "":
        c = etree.Comment(cmt)
        c.tail = val
        el.insert(0, c)
      else:
        el.text = val
      el.attrib.pop(atnm)

#### End of XMLText Class ###   