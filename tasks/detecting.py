import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Train and then run the detectors
@task
@needs(['prepareDetectors'])
def detect(options):
  call_task('train')
  call_task('runDetect')

# Train all detectors
@task
def train(options):
  call_task('trainLengths')
  call_task('trainTimings')
#  call_task('trainBow')
  call_task('trainEntropy')
  call_task('formatPredictions')

# Train the old string detector with all traces
@task
def trainEntropy(options):
  call_task('trainObfsproxyEntropy')
  call_task('trainSslEntropy')
  call_task('trainDustEntropy')

# Train the old string detector with obfs2 traces
@task
def trainObfsproxyEntropy(options):
  if os.path.exists('detectors/entropy/entropy.csv'):
    os.remove('detectors/entropy/entropy.csv')
  for filename in glob.glob('traces/test/tagged/obfsproxy/*.entropy'):
    sh('cat '+filename+' >>detectors/entropy/entropy.csv')
  with pushd('detectors/entropy'):
    sh('Rscript format.r') # generate data.txt from entropy.csv

    sh('jags entropy.jags')

    if not os.path.exists('obfsproxy'):
      os.mkdir('obfsproxy')
    sh('mv CODA*.txt obfsproxy')

# Train the old string detector with SSL traces
@task
def trainSslEntropy(options):
  if os.path.exists('detectors/entropy/entropy.csv'):
    os.remove('detectors/entropy/entropy.csv')
  for filename in glob.glob('traces/test/tagged/SSL/*.entropy'):
    sh('cat '+filename+' >>detectors/entropy/entropy.csv')
  with pushd('detectors/entropy'):
    sh('Rscript format.r') # generate data.txt from entropy.csv

    sh('jags entropy.jags')

    if not os.path.exists('SSL'):
      os.mkdir('SSL')
    sh('mv CODA*.txt SSL')

# Train the old string detector with Dust traces
@task
def trainDustEntropy(options):
  if os.path.exists('detectors/entropy/entropy.csv'):
    os.remove('detectors/entropy/entropy.csv')
  for filename in glob.glob('traces/test/tagged/Dust/*.entropy'):
    sh('cat '+filename+' >>detectors/entropy/entropy.csv')
  with pushd('detectors/entropy'):
    sh('Rscript format.r') # generate data.txt from entropy.csv

    sh('jags entropy.jags')

    if not os.path.exists('Dust'):
      os.mkdir('Dust')
    sh('mv CODA*.txt Dust')

# Train the length detector with all traces
@task
def trainLengths(options):
  call_task('trainObfsproxyLengths')
  call_task('trainSslLengths')
  call_task('trainDustLengths')

# Train the length detector with obfs2 traces
@task
def trainObfsproxyLengths(options):
  if os.path.exists('detectors/lengths/lengths.csv'):
    os.remove('detectors/lengths/lengths.csv')
  for filename in glob.glob('traces/test/tagged/obfsproxy/*.length'):
    sh('cat '+filename+' >>detectors/lengths/lengths.csv')
  with pushd('detectors/lengths'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags lengths.jags')

    if not os.path.exists('obfsproxy'):
      os.mkdir('obfsproxy')
    sh('mv CODA*.txt obfsproxy')

# Train the length detector with Dust traces
@task
def trainDustLengths(options):
  if os.path.exists('detectors/lengths/lengths.csv'):
    os.remove('detectors/lengths/lengths.csv')
  for filename in glob.glob('traces/test/tagged/Dust/*.length'):
    sh('cat '+filename+' >>detectors/lengths/lengths.csv')
  with pushd('detectors/lengths'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags lengths.jags')

    if not os.path.exists('Dust'):
      os.mkdir('Dust')
    sh('mv CODA*.txt Dust')

# Train the length detector with SSL traces
@task
def trainSslLengths(options):
  if os.path.exists('detectors/lengths/lengths.csv'):
    os.remove('detectors/lengths/lengths.csv')
  for filename in glob.glob('traces/test/tagged/SSL/*.length'):
    sh('cat '+filename+' >>detectors/lengths/lengths.csv')
  with pushd('detectors/lengths'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags lengths.jags')

    if not os.path.exists('SSL'):
      os.mkdir('SSL')
    sh('mv CODA*.txt SSL')

@task
def formatPredictions(options):
  with pushd('detectors'):
    for detector in os.listdir('.'):
      if os.path.isdir(detector):
        with pushd(detector):
          if os.path.exists('formatPredictions.r'):
            sh('Rscript formatPredictions.r')

# Train the timing detector
@task
def trainTimings(options):
  call_task('trainSslTimings')
  call_task('trainObfsproxyTimings')
  call_task('trainDustTimings')

@task
# Train the timing detector with SSL traces
def trainSslTimings(options):
  if os.path.exists('detectors/timings/timings.csv'):
    os.remove('detectors/timings/timings.csv')
  for filename in glob.glob('traces/test/tagged/SSL/*.length'):
    sh('cat '+filename+' >>detectors/timings/timings.csv')
  with pushd('detectors/timings'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags timings.jags')

    if not os.path.exists('SSL'):
      os.mkdir('SSL')
    sh('mv CODA*.txt SSL')

# Train the timing detector with obfs2 traces
@task
def trainObfsproxyTimings(options):
  if os.path.exists('detectors/timings/timings.csv'):
    os.remove('detectors/timings/timings.csv')
  for filename in glob.glob('traces/test/tagged/obfsproxy/*.length'):
    sh('cat '+filename+' >>detectors/timings/timings.csv')
  with pushd('detectors/timings'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags timings.jags')

    if not os.path.exists('obfsproxy'):
      os.mkdir('obfsproxy')
    sh('mv CODA*.txt obfsproxy')

# Train the timing detector with Dust traces
@task
def trainDustTimings(options):
  if os.path.exists('detectors/timings/timings.csv'):
    os.remove('detectors/timings/timings.csv')
  for filename in glob.glob('traces/test/tagged/Dust/*.length'):
    sh('cat '+filename+' >>detectors/timings/timings.csv')
  with pushd('detectors/timings'):
    sh('Rscript format.r') # generate data.txt from lengths.csv

    sh('jags timings.jags')

    if not os.path.exists('Dust'):
      os.mkdir('Dust')
    sh('mv CODA*.txt Dust')

# Run all of the detectors
@task
def runDetect(options):
  call_task('runLengths')
  call_task('runTimings')
#  call_task('runBow')
  call_task('runEntropy')

# Run the old string detector
@task
def runEntropy(options):
  if os.path.exists('detectors/entropy/files.csv'):
    os.remove('detectors/entropy/files.csv')
  f=open('detectors/entropy/files.csv', 'wb')
  for traceDir in os.listdir('traces'):
    for protocol in os.listdir('traces/'+traceDir+'/tagged'):
      for tracefile in glob.glob('traces/'+traceDir+'/tagged/'+protocol+'/*.entropy'):
        f.write('../../'+tracefile+"\n")
  f.close()

  with pushd('detectors/entropy'):
    sh('Rscript detectEntropy.r')
    sh('python fixOutput.py')

# Run the length detector
@task
def runLengths(options):
  if os.path.exists('detectors/lengths/files.csv'):
    os.remove('detectors/lengths/files.csv')
  f=open('detectors/lengths/files.csv', 'wb')
  for traceDir in os.listdir('traces'):
    for protocol in os.listdir('traces/'+traceDir+'/tagged'):
      for tracefile in glob.glob('traces/'+traceDir+'/tagged/'+protocol+'/*.length'):
        f.write('../../'+tracefile+"\n")
  f.close()

  with pushd('detectors/lengths'):
    sh('python detectLengths.py')

# Run the bag of words string detector
@task
def runBow(options):
  import csv
  from process import extractWords
  from detectors.bow.detectLSI import LsiDetector

  lsi=LsiDetector()

  if not os.path.exists('traces'):
    return
  with pushd('traces'):
    for tracedir in os.listdir('.'):
      if not os.path.isdir(tracedir):
        continue
      with pushd(tracedir):
        if not os.path.exists('tagged'):
          continue
        with pushd('tagged'):
          f=open('../../../detectors/bow/output.csv', 'wb')
          writer=csv.writer(f)
          writer.writerow(['file','decision','truth','correct'])

          for tag in os.listdir('.'):
            with pushd(tag):
              for streamfile in glob.glob('*.pcap'):
                words=extractWords(streamfile, [])
                newtag=lsi.classify(words)
                print(tag+' ?= '+newtag)
                writer.writerow([streamfile, newtag, tag, int(newtag==tag)])

          f.close()

# Run the timings detector
@task
def runTimings(options):
  with pushd('detectors/timings'):
    sh('python detectTimings.py')
