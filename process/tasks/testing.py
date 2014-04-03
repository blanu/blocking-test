import os
import sys
import shutil

from paver.easy import *
from paver.path import *

from sets import Set

from util import load

sys.path.append(os.path.abspath('.'))

expectedPorts=Set([22, 25, 554, 3306, 5222, 5269, 5280, 7777])

def safe_task(name, options):
  print("Execuring task %s. Please wait." % (name))
  try:
    call_task(name)
    print("Task %s completed successfully" % (name))
  except Exception, e:
    print("Error running task %s: %s" % (name, str(e)))
  print('')

@task
def all(options):
  safe_task('nmap')
  safe_task('compile', options)

@task
def ls(options):
  sh('fab -f src/fabfile.py -H against@162.209.102.232 list')

@task
def update(options):
  sh('fab -f src/fabfile.py -H against@162.209.102.232 update')

@task
def sync(options):
  sh('rsync -v -a --include "*.zip" --exclude "*" "against@162.209.102.232:." datasets')

@task
@consume_args
def inspect(args):
  f=args[0]
  if os.path.exists('datasets/'+f+'.zip'):
    if os.path.exists('traces'):
      print('Removing traces')
      shutil.rmtree('traces')
    sh('unzip datasets/'+f+'.zip')
    print('Writing dataset id')
    wf=open('traces/dataset.id', 'w')
    wf.write(f+"\n")
    wf.close()
  else:
    print('Unknown dataset '+f)

@task
def nmap(options):
  if os.path.exists('traces/dataset.id'):
    f=open('traces/dataset.id')
    setid=f.readline().strip()
    f.close()
  else:
    print('Dataset has no id')
    return
  if os.path.exists('traces/nmap.txt'):
    f=open('traces/nmap.txt')
    lines=f.readlines()[6:-2]
    ports=Set(map(extractPort, lines))
    blocked=list(expectedPorts.difference(ports))
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/nmap' % (setid), 'w')
    if len(blocked)==0:
      wf.write("None")
    else:
      wf.write(','.join(blocked))
    wf.write("\n")
    wf.close()
    print("Found %d blocked ports with nmap" % (len(blocked)))
  else:
    print('No nmap data found')

def extractPort(line):
  return int(line.strip().split('/')[0])

@task
def compile(options):
  pass

