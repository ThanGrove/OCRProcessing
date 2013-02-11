# coding=utf-8

import codecs
from lxml import etree
from copy import deepcopy
from . import XMLVars, XMLText

#### XMLCat Class   ####
class XMLCat():
  """A class for processing an XML document that is a list of texts.
     The XML expected here is based on the simple schema for mapping from an Excell document, Peltsek_Excell_Datamap.xsd
     This is a <spreadsheet> element with a series of <textrecord>s in it. Each text record has the following children:
       tnum, key, title, vnum, startpage, endpage, numofchaps, chaptype, doxography, translators, crossrefs, notes """
       
  docpath = ""
  tree = None
  name = ""
  vols = {}
  texts = {}
  textcount = 0
  volcount = 0
  
  def __init__(self, path, name):
    """Takes a path to an XML document and parse it, creating two dictionary attributes: 
        1. vols = an dictionary of volumes keyed on vol num and 2. texts a dictionary of texts keyed on text num"""
    try:
      self.name = name
      seqvnum = 0
      oldvnum = 0
      done = False
      
      # Load XML doc and perform xpath search for text elements
      self.tree = etree.parse(path)
      root = self.tree.getroot()
      textels = root.xpath('/*//' + XMLVars.textelement)
      
      # Iterate through the text elements found in the XML doc
      for txt in textels:
        vnum = txt.find(XMLVars.vnumelement).text  # volume number in catalog
        if vnum != oldvnum:                    # sequential volume number
          seqvnum += 1
          oldvnum = vnum
        
        # Calculate sequential numbering by counting number of preceding text elements
        pt = txt.itersiblings(tag=XMLVars.textelement, preceding=True) 
        tnum = len(list(pt)) + 1 # calculate text number as number of preceding siblings plus one
        
        # Add the text to the volumes text list or else start a new vol text list
        if seqvnum in self.vols:
          self.vols[seqvnum].append(tnum)
        else:
          self.vols[seqvnum] = [tnum]
          
        # If there is no ID element with sequential number then add one
        if txt.find(XMLVars.idel) == None:
          se = etree.Element(XMLVars.idel)
          se.text = unicode(str(tnum))
          txt.find("tnum").addprevious(se)
          
        # Add the element to the text list using its sequential number as id
        self.texts[tnum] = txt
        
      # set the object's textcount and volcount
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
    
  def getText(self, n, type="object"):
    """Returns a text object"""
    if self.texts.has_key(n):
      if type == "element":
        return self.texts[n]
      else:
        return XMLText.TextCat(self.texts[n])
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
      yield XMLText.TextCat(txt)
      
  def getTextList(self, type="tuple"):
    """Get a list of texts in one of three formats: tuples (default), arrays, or dictionaries"""
    out = []
    for t in self.iterTexts():
      if type == "array":
        out.append([t.key, t.tnum, t.title, t.vnum, t.startpage, t.endpage, t.numofchaps, t.chaptype,
                  t.doxography, t.translators, t.crossrefs, t.notes])
      elif type == "dictionary":
        out.append({ "key": t.key, "tnum": t.tnum, "title": t.title,
                    "vnum": t.vnum, "startpage": t.startpage, "endpage": t.endpage,
                    "numofchaps": t.numofchaps, "chaptype": t.chaptype,
                    "doxography": t.doxography, "translators": t.translators,
                    "crossrefs": t.crossrefs, "notes": t.notes})
      else:
        out.append((t.key, t.tnum, t.title, t.vnum, t.startpage, t.endpage, t.numofchaps, t.chaptype,
                  t.doxography, t.translators, t.crossrefs, t.notes))
    return out
  
  def write(self, path):
    fout = codecs.open(path, 'w', encoding='utf-8')
    fout.write(etree.tostring(self.tree, encoding=unicode))
    fout.close()
  
#### End of XMLCat Class ###
