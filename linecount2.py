# coding=utf-8
import sys
import codecs
fname = sys.argv[1]
f = codecs.open(fname, 'r', encoding='utf-8')
lct = 0
words = [[u'ཆོས',0], [u'སྤྱོད',0]]
for w in words:
  print w,
