import os
import sys
import math
import random
import hashlib

sys.path.append(os.path.abspath('../..'))

from util import load

def mean(a):
  return float(sum(a))/float(len(a))

def dev(a, b):
  total=0
  for x in range(1500):
    diff=abs(a[x]-b[x])
    total=total+diff
  return total

def count(a, k):
  histogram = [1] * k
  for x in a:
    x=x[0]
    histogram[x-1] += 1
  return histogram

def mkdata(lengths):
  k = max(1500, max(map(len, lengths)))
  data=count(lengths, k)

  return data

labels=['obfsproxy', 'SSL', 'Dust']

res1=load('obfsproxy.csv', int)
res2=load('SSL.csv', int)
res3=load('Dust.csv', int)

files=load('files.csv')

d1s=[]
d2s=[]
decisions=[]

f=open('output.csv', 'wb')
for file in files:
  file=file[0]
  correct=file.split('/')[-2]
  if correct=='http':
    continue
  print('correct: '+str(correct))
  lengths=load(file, int)
  data=mkdata(lengths)

#  res1=[res1[0]]
#  res2=[res2[0]]
#  res3=[res3[0]]

  devs=[]
  for i in range(len(res1)):
    devs.append(dev(data, res1[i]))
  d1=math.log(mean(devs))

  devs2=[]
  for i in range(len(res2)):
    devs2.append(dev(data, res2[i]))
  d2=math.log(mean(devs2))

  devs3=[]
  for i in range(len(res3)):
    devs3.append(dev(data, res3[i]))
  d3=math.log(mean(devs3))

  ds=[d1,d2,d3]
  md=min(ds)
  di=ds.index(md)
  decision=labels[di]
  print(decision)

  f.write('lengths,'+str(file)+','+str(d1)+','+str(d2)+','+str(d3)+','+str(decision)+','+str(correct)+','+str(int(decision==correct))+"\n")
f.close()
