# coding=utf-8

from lxml import etree
from . import Vars

####  THLText Class ####
class Text(object):
  """THL Text: An Object for manipulating XML data about one text in a catalog"""
  
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
    for p in Vars.textprops:
      setattr(self, p, t.find(p).text)
  
  def __type__(self):
    return "THL Text"
  
  def JSON(self):
    """Returns a unicode JSON object of the text's attributes""" 
    out = u'{"' # Open JSON object
    kvsep = u'":"'  # Separator between key and value
    itemsep = u'", "' # Separator between items
    for p in Vars.textprops: # loop through attributes from props list
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