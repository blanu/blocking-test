# This is a set of tasks for processing the output of the detectors.

import os

from paver.easy import *
from paver.path import *

from util import load

sys.path.append(os.path.abspath('.'))

# Combine the output of the various detectors into one combined output file.
@task
def combine(options):
  if not os.path.exists('output'):
    os.mkdir('output')
  if os.path.exists('output/combined.csv'):
    os.remove('output/combined.csv')
  for detector in os.listdir('detectors'):
    if os.path.exists('detectors/'+detector+'/output.csv'):
      sh('cat detectors/'+detector+'/output.csv >>output/combined.csv')

# Generate scores for encoders and detectors based on the combined output file
@task
@needs(['combine'])
def score(options):
  if not os.path.exists('output/combined.csv'):
    return
  if os.path.exists('output/results.csv'):
    os.remove('output/results.csv')
  data=load('output/combined.csv', False)
  detectors={}
  encoders={}
  for row in data:
    detector, tracename, d1, d2, d3, guess, answer, correct=row
    if guess==answer:
      if detector in detectors.keys():
        stats=detectors[detector]
        stats[0]=stats[0]+1
        detectors[detector]=stats
      else:
        detectors[detector]=[1,0]
      if answer in encoders.keys():
        stats=encoders[answer]
        stats[0]=stats[0]+1
        encoders[answer]=stats
      else:
        encoders[answer]=[1,0,0]
    else:
      if detector in detectors.keys():
        stats=detectors[detector]
        stats[1]=stats[1]+1
        detectors[detector]=stats
      else:
        detectors[detector]=[0,1]
      if guess in encoders.keys():
        stats=encoders[guess]
        stats[1]=stats[1]+1
        encoders[guess]=stats
      else:
        encoders[guess]=[0,1,0]
      if answer in encoders.keys():
        stats=encoders[answer]
        stats[2]=stats[2]+1
        encoders[answer]=stats
      else:
        encoders[answer]=[0,0,1]

  f=open('output/detectors.csv', 'wb')
  for detector in detectors:
    stats=detectors[detector]
    f.write(detector+','+str(stats[0])+','+str(stats[1])+"\n")
  f.close()
  f=open('output/encoders.csv', 'wb')
  for encoder in encoders:
    stats=encoders[encoder]
    f.write(encoder+','+str(stats[0])+','+str(stats[1])+','+str(stats[2])+"\n")
  f.close()

# Generate scores for encoders and detectors based on the combined output file
@task
@needs(['combine'])
def diffScore(options):
  diffs={
    'Dust-obfsproxy': [0,0],
    'Dust-SSL': [0, 0],
    'obfsproxy-SSL': [0,0]
  }

  if not os.path.exists('output/combined.csv'):
    return
  if os.path.exists('output/diff.csv'):
    os.remove('output/diff.csv')
  data=load('output/combined.csv', False)
  for row in data:
    detector, tracename, d1, d2, d3, guess, answer, correct=row
    if guess==answer:
      if answer=='obfsproxy':
        diffs['Dust-obfsproxy'][0]=diffs['Dust-obfsproxy'][0]+1
        diffs['obfsproxy-SSL'][0]=diffs['obfsproxy-SSL'][0]+1
      elif answer=='SSL':
        diffs['Dust-SSL'][0]=diffs['Dust-SSL'][0]+1
        diffs['obfsproxy-SSL'][0]=diffs['obfsproxy-SSL'][0]+1
      elif answer=='Dust':
        diffs['Dust-obfsproxy'][0]=diffs['Dust-obfsproxy'][0]+1
        diffs['Dust-SSL'][0]=diffs['Dust-SSL'][0]+1
      else:
        print('Unknown answer: '+str(answer))
    else:
      if answer=='obfsproxy' and guess=='SSL':
        diffs['obfsproxy-SSL'][1]=diffs['obfsproxy-SSL'][1]+1
      elif answer=='obfsproxy' and guess=='Dust':
        diffs['Dust-obfsproxy'][1]=diffs['Dust-obfsproxy'][1]+1
      elif answer=='SSL' and guess=='obfsproxy':
        diffs['obfsproxy-SSL'][1]=diffs['obfsproxy-SSL'][1]+1
      elif answer=='SSL' and guess=='Dust':
        diffs['Dust-SSL'][1]=diffs['Dust-SSL'][1]+1
      elif answer=='Dust' and guess=='obfsproxy':
        diffs['Dust-obfsproxy'][1]=diffs['Dust-obfsproxy'][1]+1
      elif answer=='Dust' and guess=='SSL':
        diffs['Dust-SSL'][1]=diffs['Dust-SSL'][1]+1
      else:
        print('Unknown answer or guess: '+str(answer)+' '+str(guess))

  f=open('output/diffs.csv', 'wb')
  for diff in diffs:
    stats=diffs[diff]
    f.write(diff+','+str(stats[0])+','+str(stats[1])+"\n")
  f.close()

# Generate scores for encoders and detectors based on the combined output file
@task
@needs(['score'])
def errorRate(options):
  if not os.path.exists('output/detectors.csv'):
    return
  data=load('output/detectors.csv', False)
  for row in data:
    detector, correct, incorrect=row
    correct=float(correct)
    incorrect=float(incorrect)
    total=correct+incorrect
    pc=int(round((correct*100)/total))
    print(detector+': '+str(pc)+'% detected')

  print('')

  if not os.path.exists('output/encoders.csv'):
    return
  data=load('output/encoders.csv', False)
  for row in data:
    encoder, correct, fpos, fneg=row
    correct=float(correct)
    fpos=float(fpos)
    fneg=float(fneg)
    total=correct+fpos+fneg
    pc=round((correct*100)/total)
    pp=round((fpos*100)/total)
    pn=round((fneg*100)/total)
    print(encoder+': '+str(int(pc))+'% ('+str(int(pp))+'%/'+str(int(pn))+'%) detected')

  print('')

  if not os.path.exists('output/diffs.csv'):
    return
  data=load('output/diffs.csv', False)
  for row in data:
    pair, correct, incorrect=row
    correct=float(correct)
    incorrect=float(incorrect)
    total=correct+incorrect
    pc=int(round((correct*100)/total))
    print(pair+': '+str(pc)+'% distinguishable')
