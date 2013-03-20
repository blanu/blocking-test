# util.py contains utility functions used by paver tasks defined in pavement.py.

import csv

# Changes extension of filename, used by trace extractors
def changeExt(filename, ext):
  if '.' in filename:
    parts=filename.split('.')[:-1]
    parts.append(ext)
    return '.'.join(parts)
  else:
    return filename+'.'+ext

def load(filename, convert=None):
  f=open(filename, 'rb')
  reader = csv.reader(f)
  results=[]
  for row in reader:
    if convert:
      results.append(map(convert, row))
    else:
      results.append(row)
  f.close()
  return results
