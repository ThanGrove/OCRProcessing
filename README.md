######################  OCRProcessing Scripts ##############################

Author: Than Grove
Date: Feb 8, 2013

These are scripts I am creating to process the OCR XML output of Tibetan scanning of NGB made by Zach.
The OCR output comes as one XML file (with .txt extension) per volume of a collection.

The goal of these scripts is

  1.  to create a process whereby given the catalog data it will break up the
      individual volume files into text files that will contain the XML marked up
      file for each text. This process will assign each text a unique sequential id.
      
  2.  to create the individual bibl records for each text named with the text id.
  
  3.  to create an XML file that encodes the catalog hierarchy (cat->vol->text) in the TEI Tibbibl
      markup devised for the THL system that will reference the text files and bibl files made above.

