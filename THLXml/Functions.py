
def loadPeltsek():
  catpath = join(data_path, 'peltsek-with-lines.xml')
  cat = Catalog(catpath, 'Peltsek')
  cat.importVolInfo(join(data_path, 'ngb-pt-vols.xml'))
  return cat

def getDateTime():
  import time
  ltime = time.localtime(time.time())
  datearr = [str(ltime[0]), str(ltime[1]).zfill(2), str(ltime[2]).zfill(2)]
  timearr = [str(ltime[3] - 5).zfill(2), str(ltime[4]).zfill(2), str(ltime[5]).zfill(2)]
  dtstr = "-".join(datearr) + "-" + "".join(timearr)
  return dtstr