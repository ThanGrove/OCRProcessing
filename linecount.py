# coding=utf-8
import sys
import codecs
fname = sys.argv[1]
f = codecs.open(fname, 'r', encoding='utf-8')
lct = 0
words = {u'ཆོས':0, u'སྤྱོད':0, u'མཉམ':0, u'བྱུང་':0, u'ཡང་':0}
for line in f:
  lct = lct + 1
  for w, c in words.iteritems():
    c = c + line.count(w)
    words[w] = c
print "There are {0} lines".format(lct)
f.close()
ct = 0
for w, c in words.iteritems():
  ct = ct + 1
  print "Word {0} was found {1} times".format(ct,c)
print "Bye!"