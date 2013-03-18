import os
import sys

sys.path.append(os.path.abspath('../..'))

from util import load

data=load('output.csv', False)
f=open('output.csv', 'wb')
for row in data:
  tracename, d1, d2, d3, guess=row
  parts=tracename.split('/')
  answer=parts[-2]
  if answer=='http':
    continue
  f.write('entropy,'+tracename+','+d1+','+d2+','+d3+','+guess+','+answer+','+str(int(guess==answer))+"\n")
f.close()