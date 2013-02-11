# coding=utf-8

class XMLCommonVars:
  # text, vnum, and tnum elements: variables that holds the name of the those respective tags
  textelement = "textrecord"   # element that holds a texts data
  vnumelement = "vnum"         # element with the volume number
  mytnumel = "tnum"            # element with the text number (sequentiall from the beginning)
  # textprops: a list of all property names (= child elements) of a text record
  textprops = ["tnum", "key", "title", "vnum", "startpage", "endpage", "numofchaps", "chaptype", "doxography", "translators", "crossrefs", "notes"]