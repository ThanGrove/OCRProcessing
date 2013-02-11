# coding=utf-8
import XMLCommonVars
from lxml import etree
from copy import deepcopy

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
  
  def load(self, path, name):
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
    
  def getText(self, n, type="object"):
    """Returns a text object"""
    if self.texts.has_key(n):
      if type == "element":
        return self.texts[n]
      else:
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
