import os
import sys
import shutil

from paver.easy import *
from paver.path import *

from sets import Set
from numpy import mean, std

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
    intercepted=list(ports.difference(expectedPorts))
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/nmap-blocked.csv' % (setid), 'w')
    wf.write("Blocked Port\n")
    if len(blocked)!=0:
      wf.write("\n".join(map(str,blocked)))
    wf.write("\n")
    wf.close()

    wf=open('analysis/%s/nmap-intercepted.csv' % (setid), 'w')
    wf.write("Intercepted Port\n")
    if len(intercepted)!=0:
      wf.write("\n".join(map(str,intercepted)))
    wf.write("\n")
    wf.close()

    print("Found %d blocked ports with nmap" % (len(blocked)))
    print("Found %d intercepted ports with nmap" % (len(intercepted)))
  else:
    print('No nmap data found')

def extractPort(line):
  return int(line.strip().split('/')[0])

@task
def ping(options):
  if os.path.exists('traces/dataset.id'):
    f=open('traces/dataset.id')
    setid=f.readline().strip()
    f.close()
  else:
    print('Dataset has no id')
    return
  if os.path.exists('traces/ping.txt'):
    f=open('traces/ping.txt')
    lines=f.readlines()[1:]
    times=map(extractTime, lines)
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/ping.csv' % (setid), 'w')
    wf.write("Ping time\n")
    if len(times)!=0:
      wf.write("\n".join(map(str,times)))
      wf.write("\n")
    wf.close()

    wf=open('analysis/%s/ping-summary.csv' % (setid), 'w')
    wf.write("Average,Standard Deviation\n")
    tm=mean(times)
    ts=std(times)
    wf.write(str(tm)+","+str(ts)+"\n")
    wf.close()
    print("Found %d times with ping" % (len(times)))
  else:
    print('No ping data found')

def extractTime(line):
  return float(line.strip().split(' ')[-2].split('=')[1])

@task
def traceroute(options):
  if os.path.exists('traces/dataset.id'):
    f=open('traces/dataset.id')
    setid=f.readline().strip()
    f.close()
  else:
    print('Dataset has no id')
    return
  if os.path.exists('traces/traceroute.txt'):
    f=open('traces/traceroute.txt')
    lines=f.readlines()[1:]
    probes=map(extractTraceroute, lines)
    probes=filter(lambda x: x!=None, probes)
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/traceroute.csv' % (setid), 'w')
    wf.write("AS,Host,Probe 1, Probe 2, Probe 3\n")
    for probe in probes:
      wf.write(','.join(map(str,probe))+"\n")
    wf.close()
    print("Found %d probes with traceroute" % (len(probes)))
  else:
    print('No traceroute data found')

def extractTraceroute(line):
  if '*' in line:
    return None

  (count, host, p1, p2, p3)=line.strip().split('  ')
  parts=host.split(' ')
  if '[' in host: # AS enabled
    AS=parts[0][1:-1]
    host=parts[2][1:-1]
  else:
    AS='unknown'
    host=parts[1][1:-1]
  p1=float(p1.split(' ')[0])
  p2=float(p2.split(' ')[0])
  p3=float(p3.split(' ')[0])
  return (AS, host, p1, p2, p3)

@task
def http(options):
  nose('http')

@task
def https(options):
  nose('https')

def nose(protocol):
  if os.path.exists('traces/dataset.id'):
    f=open('traces/dataset.id')
    setid=f.readline().strip()
    f.close()
  else:
    print('Dataset has no id')
    return
  if os.path.exists("traces/generate-%s.txt" % (protocol)):
    f=open("traces/generate-%s.txt" % (protocol))
    lines=f.readlines()
    results=map(parseNose, list(lines[0].strip()))
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/generate-%s.csv' % (setid, protocol), 'w')
    wf.write("Test Success\n")
    for result in results:
      wf.write(result+"\n")
    wf.close()
    print("Found %d pages with %s" % (len(results), protocol))
  else:
    print("No %s data found" % (protocol))

def parseNose(char):
  if char=='.':
    return 'Success'
  elif char=='E':
    return 'Failure'
  else:
    return 'Unknown'

@task
def compile(options):
  pass

