# coding=utf-8
import os
import codecs
from lxml import etree
from copy import deepcopy
from . import Vars, Text
from os import listdir
from os.path import dirname, join
from urllib import urlopen, urlencode
from re import search
from datetime import date
import time

my_path = dirname(__file__)
tmpl_path = join(my_path, 'templates')
data_path = join(my_path, '..', 'data')
vol_dir = join(my_path, '..', '..', 'volsource') # directory which contains OCR volume files

#### Catalog Class   ####
class Catalog():
  """A class for processing an XML document that is a list of texts.
     The XML expected here is based on the simple schema for mapping from an Excell document, Peltsek_Excell_Datamap.xsd
     This is a <spreadsheet> element with a series of <textrecord>s in it. Each text record has the following children:
       tnum, key, title, vnum, startpage, endpage, numofchaps, chaptype, doxography, translators, crossrefs, notes """
       
  docpath = ""
  tree = None
  colname = {
    "eng":"",
    "tib":"",
    "wyl":""
  }
  coll = ""
  sigla = ""
  vols = {}
  texts = {}
  textcount = 0
  volcount = 0
  voldir = ""
  
  def __init__(self, path, name, voldir = vol_dir):
    """Takes a path to an XML document and parse it, creating two dictionary attributes: 
        1. vols = an dictionary of volumes keyed on vol num and 2. texts a dictionary of texts keyed on text num"""
    try:
      self.name = name
      self.voldir = voldir
      seqvnum = 0
      oldvnum = 0
      done = False
      
      # Load XML doc and perform xpath search for text elements
      self.tree = etree.parse(path)
      root = self.tree.getroot()
      textels = root.xpath('/*//' + Vars.textelement)
      
      # Iterate through the text elements found in the XML doc
      for txt in textels:
        vnum = txt.find(Vars.vnumelement).text  # volume number in catalog
        if vnum != oldvnum:                    # sequential volume number
          seqvnum += 1
          oldvnum = vnum
        
        # Calculate sequential numbering by counting number of preceding text elements
        pt = txt.itersiblings(tag=Vars.textelement, preceding=True) 
        tnum = len(list(pt)) + 1 # calculate text number as number of preceding siblings plus one
        
        # Add the text to the volumes text list or else start a new vol text list
        if seqvnum in self.vols:
          self.vols[seqvnum]["texts"].append(tnum)
        else:
          self.vols[seqvnum] = { "texts":[tnum] }
          
        # If there is no ID element with sequential number then add one
        if txt.find(Vars.idel) == None:
          se = etree.Element(Vars.idel)
          se.text = unicode(str(tnum))
          txt.find("tnum").addprevious(se)
          
        # Add the element to the text list using its sequential number as id
        self.texts[tnum] = txt
        
      # set the object's textcount and volcount
      self.textcount = len(self.texts)
      self.volcount = len(self.vols)
      
      #print "Automatically fixing missing paginations and line numbers."
      #print "To disable this, comment out Catalog.py line 88 and 89."
      #self.fixMissingPaginations()
      #self.fixMissingPaginations() # hack to cover those ending paginations where there is not start pagination for following texts
    except IOError:
      print "\nError! '{0}' is not a valid file name. Cannot continue. Sorry!".format(path)
      
  def __type__(self):
    return "THL Catalog"
  
  # General Functions
  def write(self, path, outtype="simple", doc="self"):
    """Function to write either the catalog, volume tocs or volume bibls"""
    if outtype == "simple":
      if doc == "self":
        doc = self.tree
      fout = codecs.open(path, 'w', encoding='utf-8')
      fout.write(etree.tostring(doc, encoding=unicode))
      fout.close()
      
    # vols outtype produces a div structure of volumes in TEI format
    elif outtype == "vols":
      catroot = etree.Element("div", {"type":"vols"})
      voltemplate = join(tmpl_path, 'toc-vol.xml')
      txttemplate = join(tmpl_path, 'toc-text.xml')
      for k, v in self.vols.iteritems():
        vdoc = etree.parse(voltemplate).getroot()
        vid = "ngb-pt-v" + str(int(k)).zfill(3)
        print "VID is: {0}".format(vid)
        vnum = int(k)
        vdoc.set('id', vid)
        self.setTemplateVal(vdoc, '/*//title[@id="vtitle"]', "Volume {0}".format(vnum))
        vnumel = vdoc.xpath('/*//num[@id="vnum"]')[0]
        vnumel.set('n',v['wylie'])
        vnumel.set('value', str(vnum))
        vnumel.text = v['tib']
        vnumel.attrib.pop("id")
        self.setTemplateVal(vdoc, '/*//num[@id="starttxt"]', v['texts'][0])
        self.setTemplateVal(vdoc, '/*//num[@id="endtxt"]', v['texts'][-1])
        for txt in self.getVolumeTOC(k, 'list'):
          tdoc = etree.parse(txttemplate).getroot()
          tid = "ngb-pt-{0}".format(txt["key"].zfill(4))
          tdoc.set("id",tid)
          title = txt["title"]
          self.setTemplateVal(tdoc, '/*//title[@id="tibtitle"]', title)
          self.setTemplateVal(tdoc, '/*//title[@id="wylietitle"]', self.tibToWylie(title))
          self.setTemplateVal(tdoc, '/*//idno[@id="tid"]', txt["key"].zfill(4))
          if txt["start"] is not None:
            stpg = txt["start"].split('.')
            self.setTemplateVal(tdoc, '/*//num[@id="stpg"]', stpg[0])
            if len(stpg) == 2:
              self.setTemplateVal(tdoc, '/*//num[@id="stln"]', stpg[1])
            else:
              self.setTemplateVal(tdoc, '/*//num[@id="stln"]', "1")
          else:
            self.removeAttributes(tdoc, 'id', ['stpg', 'stln'])
          if txt["end"] is not None:
            endpg = txt["end"].split('.')
            self.setTemplateVal(tdoc, '/*//num[@id="endpg"]', endpg[0])
            if len(endpg) == 2:
              self.setTemplateVal(tdoc, '/*//num[@id="endln"]', endpg[1])
            else:
              self.setTemplateVal(tdoc, '/*//num[@id="endln"]', "6")
          else:
            self.removeAttributes(tdoc, 'id', ['endpg', 'endln'])
          vdoc.append(tdoc)
        catroot.append(vdoc)
      fout = codecs.open(path, 'w', encoding='utf-8')
      fout.write(etree.tostring(catroot, encoding=unicode))
      fout.close()
      
    # Output of volume bibls using template
    elif outtype == "volbibs":
      voltemplate = join(tmpl_path, 'volbib.xml')
      for k, v in self.vols.iteritems():
        vdoc = etree.parse(voltemplate).getroot()
        vid = "ngb-pt-v" + str(int(k)).zfill(3)
        print "VID is: {0}".format(vid)
        vnum = int(k)
        vdoc.set('id', vid)
        self.setTemplateVal(vdoc, '/*//sysid[@id="sysid"]',vid)
        self.setTemplateVal(vdoc, '/*/controlinfo/date', str(date.today()))
        self.setTemplateVal(vdoc, '/*//tibid[@id="vid"]',k)
        self.setTemplateVal(vdoc, '/*//altid[@id="vlet"]',v['tib'],v['wylie'])
        self.setTemplateVal(vdoc, '/*//rs[@id="vollabel"]',u"༼" + v['tib'] + u"༽")
        self.setTemplateVal(vdoc, '/*//divcount[@id="texttotal"]',v['tcount'])
        self.setTemplateVal(vdoc, '/*//extent[@id="textfirst"]',"Pt." + str(v['texts'][0]))
        self.setTemplateVal(vdoc, '/*//extent[@id="textlast"]',"Pt." + str(v['texts'][-1]))
        self.setTemplateVal(vdoc, '/*//extent[@id="sides"]',v['lastpage'])
        self.setTemplateVal(vdoc, '/*//num[@id="pagelast"]',v['lastpage'])
        fout = codecs.open(join(path, vid + "-bib.xml"), 'w', encoding='utf-8')
        fout.write(etree.tostring(vdoc, encoding=unicode))
        fout.close()
        
  # Volume Functions
  def importVolInfo(self, path):
    voldoc = etree.parse(path).getroot()
    volels = voldoc.xpath('/*//volume')
    for vol in volels:
      vnum = int(vol.find('num').text)
      vobj = self.getVolume(vnum)
      if vobj != None:
        vobj['wylie'] = vol.find('name[@lang="wylie"]').text
        vobj['tib'] = vol.find('name[@lang="tib"]').text
        vobj['dox'] = vol.find('dox').text
        vobj['tcount'] = vol.find('textcount').text
        vsstr = "vol" + str(vnum).zfill(2)
        lasttext = self.getText(vobj['texts'][-1])
        if lasttext:
          vobj['lastpage'] = int(float(lasttext.endpage))
        for f in listdir(self.voldir):
          if vsstr in f:
            vobj['ocrfile'] = join(self.voldir, f)
            break
  
  def fixMissingPaginations(self):
    """This function inserts missing paginations based on the previous or subsequent texts' paginations"""
    # First fix problem with start page
    spct = 0
    enct = 0
    nofix = 0
    tlist = {}
    for tn in self.texts:
      ptxt = self.texts[tn - 1] if tn > 1 else None
      ntxt = self.texts[tn + 1] if tn < len(self.texts) else None
      t = self.texts[tn]
      tid = t.find("key").text
      
      # Fix Start pages
      startpg = t.find("startpage").text
      if isinstance(startpg, str):
        # if no line number for start page assume, get line from prev text if page same
        # otherwise assume line .1
        linenm = ".1"
        if not "." in startpg:
          if ptxt is not None:
            pend = ptxt.find("endpage").text
            if isinstance(pend, str) and "." in pend:
              pendpts = pend.split('.')
              if pendpts[0] == startpg and len(pendpts) > 1:
                linenm = "." + pendpts[1]
              elif int(pendpts[0]) == int(startpg) - 1 and int(pendpts[1]) == 6:
                linenm = ".1"
          t.find("startpage").text = startpg + linenm
          spct += 1
          tlist[tid] = 1
      elif ptxt is not None:
          # if no page number then get it from the previous texts ending
          pend = ptxt.find("endpage").text
          if pend:
            if ".6" in pend: # if previous text ends at .6 assume this test starts at .1 of next page
              pend = str(int(float(pend)) + 1) + ".1"
            t.find("startpage").text = pend
            spct += 1
            tlist[tid] = 1
      else:
        print "text {0} has no start page and can't find previous text".format(tid)
        nofix += 1
        
      # Fix End pages
      endpage = t.find("endpage").text
      if isinstance(endpage, str):
        # if not end line number get from next text start page if the same page
        # else assume line 6
        linenm = ".6"
        if not "." in endpage:
          if ntxt is not None:
            nst = ntxt.find("startpage").text
            if isinstance(nst, str) and "." in nst:
              nstpts = nst.split('.')
              if nstpts[0] == endpage and len(nstpts) > 1:
                linenm = "." + nstpts[1]
              if int(nstpts[0]) == int(endpage) + 1 and int(nstpts[1]) == 1:
                linenm = ".6"
          t.find("endpage").text = endpage + linenm
          enct += 1
          tlist[tid] = 1
      elif ntxt is not None:
          nstart = ntxt.find("startpage").text
          if nstart:
            if ".1" in nstart or "." not in nstart:
              nstart = str(int(float(nstart)) - 1) + ".6" # if next text starts at .1, assume this ends .6 of previous page
            t.find("endpage").text = nstart
            enct += 1
            tlist[tid] = 1
      else:
        print "text {0} has no end page and can't find next text".format(tid)
        nofix += 1
        
   # print "Startpages changed: {0}".format(spct)
    #print "Endpages changed: {0}".format(enct)
    #print "Missing pages unable to change: {0}".format(nofix)
    #print "Total text records changed: {0}".format(len(tlist))
    #print "Texts changed: "
    #knum = 0
    #for k in sorted(tlist.iterkeys(), key=int):
    #  print k.zfill(3),
    #  knum += 1
    #  if knum % 10 == 0:
    #    print ""
    #print ""
    
  def getVolume(self, n):
    n = int(n)
    if self.vols.has_key(n):
      return self.vols[n]
    else:
      return None
  
  def getVolumeTOC(self, n, method='plain'):
    voltoc = []
    if self.vols.has_key(n):
      vol = self.getVolume(n)
      for tn in vol["texts"]:
        txt = self.getText(tn)
        if method == 'list':
          voltoc.append({"key":txt.key, "tnum":txt.tnum, "title":txt.title, "vnum":txt.vnum, "start":txt.startpage, "end":txt.endpage})
        elif method == 'texts':
          voltoc.append(self.getText(txt.key))
        else:
          title = self.tibToWylie(txt.title)
          print txt.key, txt.tnum, wytitle, txt.vnum, txt.startpage, txt.endpage
    else:
      print "There is no volume {0}".format(n)
    if method != 'plain':
      return voltoc
    
  # Text functions
  def getText(self, n, type="object"):
    """Returns a text object"""
    if isinstance(n,str):
      n = int(n)
    if self.texts.has_key(n):
      if type == "element":
        return self.texts[n]
      elif type == "string":
        return etree.tostring(self.texts[n], encoding=unicode)
      else:
        return Text.Text(self.texts[n], self)
    else:
      return None
  
  def getTextList(self, listtype="tuple", tibformat="unicode"):
    """Get a list of texts in one of three formats: tuples (default), arrays, or dictionaries"""
    out = []
    for t in self.iterTexts():
      out.append(t.getData(listtype, tibformat))
    return out
      
  def iterTexts(self):
    txts = self.texts
    for k, txt in txts.iteritems():
      yield Text.Text(txt, self)
      
  def iterVolumes(self):
    vols = self.vols
    for k, v in vols.iteritems():
      yield v
    
  def tibToWylie(self, txt):
    url = 'http://local.thlib.org/cgi-bin/thl/lbow/wylie.pl?'  # Only Local
    q = {'conversion':'uni2wy', 'plain':'true', 'input' : unicode(txt).encode('utf-8') }
    out = ''
    fh = urlopen(url + urlencode(q))
    for l in fh.readlines():
      out += l
    fh.close()
    return out

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
        if isinstance(val, int) or isinstance(val, float):
          val = str(val)
        el.text = val
      el.attrib.pop(atnm)
  
  def removeAttributes(self, doc, att, vals):
    for v in vals:
      xp = "/*//*[@" + att + "='" + v + "']"
      els = doc.xpath(xp)
      if len(els) > 0:
        el = els[0]
        el.attrib.pop(att)
      else:
        print "Could not find attribute to remove with xpath: {0}".format(xp)
        
  
#### End of XMLCat Class ###
