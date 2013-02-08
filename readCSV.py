# coding=utf-8

#  NOT WORKING WITH UTF-8
import os
import sys
import codecs
import csv

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
        
# Get commandline parameters
finname = sys.argv[1] + '.csv'
foutname = '../output/csvtestout.txt'
outf = codecs.open(finname, 'w', encoding='utf-8')
with codecs.open(foutname, 'r', encoding='utf-8') as f:
    reader = unicode_csv_reader(f)
    print reader
    for row in reader:
      print row
      outf.write(row)