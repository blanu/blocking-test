import os
import sys
import math
import random
import hashlib

sys.path.append(os.path.abspath('../..'))

from util import load

def stoms(f):
  return long(math.floor(float(f)*1000))

def mean(a):
  return sum(a)/len(a)

def rdev(a, b):
  c=[]
  r=random.Random()
  for x in range(max(len(a),len(b))):
    ar=r.choice(a)
    br=r.choice(b)
    c.append((ar-br)**2)
  return sum(c)

def dev(a, b):
  c=[]
  for x in range(min(len(a),len(b))):
    c.append((a[x]-b[x])**2)
  return sum(c)

res1=load('obfsproxy.csv', long)
res2=load('SSL.csv', long)
res3=load('Dust.csv', long)

files=load('files.csv')

d1s=[]
d2s=[]
decisions=[]

labels=['obfsproxy', 'SSL', 'Dust']

f=open('output.csv', 'wb')
for file in files:
  file=file[0]
  correct=file.split('/')[-2]
  print('correct: '+str(correct))
  timings=load(file, stoms)
  data=[]
  for timing in timings:
    data.append(timing[0])

  devs=[]
  for i in range(len(res1)):
    devs.append(rdev(data, res1[i]))
  d1=math.log(mean(devs))

  devs2=[]
  for i in range(len(res2)):
    devs2.append(rdev(data, res2[i]))
  d2=math.log(mean(devs2))

  devs3=[]
  for i in range(len(res3)):
    devs3.append(rdev(data, res3[i]))
  d3=math.log(mean(devs3))

  ds=[d1,d2,d3]
  md=min(ds)
  di=ds.index(md)
  decision=labels[di]
  print(decision)

  f.write('timings,'+str(file)+','+str(d1)+','+str(d2)+','+str(d3)+','+str(decision)+','+str(correct)+','+str(int(decision==correct))+"\n")
f.close()
