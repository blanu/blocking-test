import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Process the trace files, extracting information for the detectors
@task
def process(options):
  call_task('streams')
  call_task('tag')
  call_task('lengths')
  call_task('timings')
  call_task('entropy')

# Extract individual streams from the traces
@task
def streams(options):
  from process import splitStreams

  if not os.path.exists('traces'):
    return
  with pushd('traces'):
    for tracedir in os.listdir('.'):
      if not os.path.isdir(tracedir):
        continue
      with pushd(tracedir):
        traces=glob.glob('*.pcap')
        if len(traces)==0:
          continue
        if not os.path.exists('streams'):
          os.mkdir('streams')
        for trace in traces:
          splitStreams(trace, 'streams')

# Tag the traces with their protocols based on their ports
@task
def tag(options):
  from process import tagStream

  if not os.path.exists('traces'):
    return
  with pushd('traces'):
    for tracedir in os.listdir('.'):
      if not os.path.isdir(tracedir):
        continue
      with pushd(tracedir):
        if not os.path.exists('streams'):
          continue
        if not os.path.exists('tagged'):
          os.mkdir('tagged')
        for stream in os.listdir('streams'):
          tagStream('streams/'+stream, 'tagged')

# Extract the old string information from the traces
@task
def strings(options):
  from process import extractStrings, extractSubstrings
  from util import changeExt

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
          for tag in os.listdir('.'):
            with pushd(tag):
              for streamfile in glob.glob('*.pcap'):
                print(streamfile)
                stringfile=changeExt(streamfile, 'string')
                extractStrings(streamfile, stringfile)
#                extractSubstrings(stringfile, changeExt(streamfile, 'string-1'), 1)
#                extractSubstrings(stringfile, changeExt(streamfile, 'string-2'), 2)
#                extractSubstrings(stringfile, changeExt(streamfile, 'string-4'), 4)

# Extract the string information from the first packet of each of the traces
@task
def firstStrings(options):
  from process import extractFirstStrings
  from util import changeExt

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
          for tag in os.listdir('.'):
            with pushd(tag):
              for streamfile in glob.glob('*.pcap'):
                print(streamfile)
                stringfile=changeExt(streamfile, 'firstString')
                extractFirstStrings(streamfile, stringfile)

# Extract the entropy information from the traces
@task
@needs(['firstStrings'])
def entropy(options):
  from process import extractStrings, extractEntropy
  from util import changeExt

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
          for tag in os.listdir('.'):
            with pushd(tag):
              for stringfile in glob.glob('*.firstString'):
                extractEntropy(stringfile, changeExt(stringfile, 'entropy'))

# Extract the bag of words string information from the traces
@task
def trainBow(options):
  from process import extractWords, saveWords, extractCorpus, saveCorpus
  from util import changeExt
  from gensim import corpora, models, similarities
  from gensim.corpora.dictionary import Dictionary

  if not os.path.exists('detectors/bow/similarity.index'):
    if os.path.exists('detectors/bow/words.dict'):
      dict=corpora.dictionary.Dictionary('detectors/bow/words.dict')
    else:
      words=[]

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
              for tag in os.listdir('.'):
                with pushd(tag):
                  for streamfile in glob.glob('*.pcap'):
                    print(streamfile)
                    words=extractWords(streamfile, words)

      saveWords(words, 'detectors/bow/words.dict')

    if os.path.exists('detectors/bow/corpus.mm'):
      corpus=corpora.MmCorpus('detectors/bow/corpus.mm')
    else:
      corpus=[]
      tags=[]
    with pushd('traces'):
      for tracedir in os.listdir('.'):
        if not os.path.isdir(tracedir):
          continue
        with pushd(tracedir):
          if not os.path.exists('tagged'):
            continue
          with pushd('tagged'):
            for tag in os.listdir('.'):
              with pushd(tag):
                if tag in tags:
                  i=tags.index(tag)
                else:
                  i=len(tags)
                  tags.append(tag)
                  corpus.append([])
                doc=[]
                for streamfile in glob.glob('*.pcap'):
                  print(streamfile)
                  doc=extractWords(streamfile, doc)
                corpus[i]=corpus[i]+doc

    for i in range(len(corpus)):
      corpus[i]=dict.doc2bow(corpus[i])

    saveCorpus(corpus, 'detectors/bow/corpus.mm')

    f=open('detectors/bow/tags.json', 'w')
    f.write(json.dumps(tags))
    f.close()

    lsi=models.LsiModel(corpus, num_topics=2)
    index=similarities.MatrixSimilarity(lsi[corpus])
    index.save('detectors/bow/similarity.index')

# Extract the length information from the traces
@task
def lengths(options):
  from process import extractLengths
  from util import changeExt

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
          for tag in os.listdir('.'):
            with pushd(tag):
              for streamfile in glob.glob('*.pcap'):
                extractLengths(streamfile, changeExt(streamfile, 'length'))

# Extract the timing information from the traces
@task
def timings(options):
  from process import extractTimings
  from util import changeExt

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
          for tag in os.listdir('.'):
            with pushd(tag):
              for streamfile in glob.glob('*.pcap'):
                extractTimings(streamfile, changeExt(streamfile, 'timing'))
