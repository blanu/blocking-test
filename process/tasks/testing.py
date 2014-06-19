import os
import sys
import shutil
import yaml
import glob

from paver.easy import *
from paver.path import *

from sets import Set
from numpy import mean, std

from util import load

sys.path.append(os.path.abspath('.'))

expectedPorts=Set([22, 25, 554, 3306, 5222, 5269, 5280, 7777])

def safe_task(name, options):
  print("Executing task %s. Please wait." % (name))
  try:
    call_task(name)
    print("Task %s completed successfully" % (name))
  except Exception, e:
    print("Error running task %s: %s" % (name, str(e)))
  print('')

@task
def all(options):
  if os.path.exists('sets.yaml'):
    f=open('sets.yaml')
    data=f.read()
    f.close()

    sets=yaml.load(data)

    for setid in sets:
      print('*'*10+' '+setid+' '+'*'*10)
      if set=='unknown' or set=='extra':
        continue
      if not os.path.exists('compiled'):
        os.mkdir('compiled')
      if not os.path.exists('compiled/'+setid):
        os.mkdir('compiled/'+setid)
      analyzeSet(options, sets[setid])
  else:
    print('No sets.yaml file')
    return

def analyzeSet(options, sets):
  if sets!=None and len(sets)>0:
    for set in sets:
      analyzeDataset(options, str(set))

def analyzeDataset(options, setid):
  print('Analyzing '+setid)
  if inspectDataset(setid):
    safe_task('analyze', options)  
    print('Analyzed '+setid)
  else:
    print('Failed to analyze '+setid)

  #raw_input("Continue?")
  print('')
  print('-'*80)
  print('')

@task
def analyze(options):
  safe_task('nmap', options)
  safe_task('ping', options)
  safe_task('traceroute', options)
  safe_task('http', options)
  safe_task('https', options)
  safe_task('dust_replay_http', options)

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
  inspectDataset(f)

def inspectDataset(f):
  if os.path.exists('datasets/'+f+'.zip'):
    if os.path.exists('traces'):
      print('Removing traces')
      shutil.rmtree('traces')
    try:
      sh('unzip datasets/'+f+'.zip')
      print('Writing dataset id')
      wf=open('traces/dataset.id', 'w')
      wf.write(f+"\n")
      wf.close()
      return True
    except:
      print('Error inspecting zip file')
      return False
  else:
    print('Unknown dataset '+f)
    return False

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
def dust_replay_http(options):
  if os.path.exists('traces/dataset.id'):
    f=open('traces/dataset.id')
    setid=f.readline().strip()
    f.close()
  else:
    print('Dataset has no id')
    return
  files=glob.glob('traces/dust_replay_http*.pcap')
  if len(files)>=1:
    size=os.path.getsize(files[0])
    if not os.path.exists('analysis'):
      os.mkdir('analysis')
    if not os.path.exists('analysis/'+setid):
      os.mkdir('analysis/'+setid)
    wf=open('analysis/%s/generate-dust_replay_http.csv' % (setid), 'w')
    wf.write("Test Success\n")
    wf.write(str(size)+"\n")
    wf.close()
    print("Found dust_replay_http pcap with size %d" % (size))
  else:
    print("No dust_replay_http data found")

@task
def compile(options):
  if os.path.exists('sets.yaml'):
    f=open('sets.yaml')
    data=f.read()
    f.close()

    sets=yaml.load(data)

    for setid in sets:
      if set=='unknown' or set=='extra':
        continue
      if not os.path.exists('compiled'):
        os.mkdir('compiled')
      if not os.path.exists('compiled/'+setid):
        os.mkdir('compiled/'+setid)
      if sets[setid]!=None and len(sets[setid])>0:
        compileSet(setid, map(str, sets[setid]))
      else:
        print('Empty set '+str(setid))
  else:
    print('No sets.yaml file')
    return

def compileSet(setid, datasets):
  print("Compiling set %s" % (setid))

  compilePing(setid, datasets)
  compileNmap(setid, datasets, 'blocked')
  compileNmap(setid, datasets, 'intercepted')
  compileTraceroute(setid, datasets)
  compileNose(setid, datasets, 'http')
  compileNose(setid, datasets, 'https')
  compileSizes(setid, datasets)

def filterWith(a, b, f):
  z=zip(a, b)
  wrapper=lambda t: f(t[1])
  filtered=filter(wrapper, z)
  return unzip(filtered)[0]

def filterBothWith(a, b, f):
  z=zip(a, b)
  wrapper=lambda t: f(t[1])
  filtered=filter(wrapper, z)
  l=unzip(filtered)
  if len(l)==0:
    return ([], [])
  else:
    return (list(l[0]), list(l[1]))

def unzip(l):
  return zip(*l)

def notNone(x):
  return x!=None

def compilePing(setid, datasets):
  print("   compiling ping")
  pings=map(parsePing, datasets)
  datasets, pings=filterBothWith(datasets, pings, notNone)

  if len(pings)==0:
    return

  f=open("compiled/%s/ping-summary.csv" % (setid), 'w')
  f.write(','.join(datasets)+"\n")

  avgs,stddevs=unzip(pings)
  f.write(','.join(avgs)+"\n")
  f.write(','.join(stddevs)+"\n")  
  f.close()

def parsePing(dataset):
  print("... from %s" % (dataset))
  if not os.path.exists("analysis/%s/ping-summary.csv" % (dataset)):
    return None
  f=open("analysis/%s/ping-summary.csv" % (dataset))
  pings=f.readlines()[1].strip().split(',')
  f.close()
  return pings

def compileNmap(setid, datasets, blocked):
  print("   compiling nmap %s" % (blocked))

  if blocked=='blocked':
    results=map(parseNmapBlocked, datasets)
  elif blocked=='intercepted':
    results=map(parseNmapIntercepted, datasets)
  else:
    print('Unknown nmap type '+blocked)
    return

  datasets, results=filterBothWith(datasets, results, notNone)
  if len(results)==0:
    return

  f=open("compiled/%s/nmap-%s.csv" % (setid, blocked), 'w')
  f.write('port,'+','.join(datasets)+"\n")

  portset=Set()
  for result in results:
    for item in result:
      portset.add(int(item))

  allports=sorted(list(portset))

  for port in allports:
    checks=[port]
    for result in results:
      if port in result:
        checks.append(1)
      else:
        checks.append(0)
    f.write(','.join(map(str,checks))+"\n")

  f.close()

def parseNmapBlocked(dataset):
  return parseNmap(dataset, 'blocked')

def parseNmapIntercepted(dataset):
  return parseNmap(dataset, 'intercepted')

def parseNmap(dataset, blocked):
  print("... from %s" % (dataset))
  if not os.path.exists("analysis/%s/nmap-%s.csv" % (dataset, blocked)):
    return None
  f=open("analysis/%s/nmap-%s.csv" % (dataset, blocked))
  ports=map(strip,f.readlines()[1:])
  f.close()
  return map(int,filter(lambda port: port!=None, ports))

def strip(line):
  s=line.strip()
  if s=='':
    return None
  else:
    return s

def compileTraceroute(setid, datasets):
  print("   compiling traceroute")

  results=map(parseTraceroute, datasets)
  datasets, results=filterBothWith(datasets, results, notNone)
  if len(results)==0:
    return

  f=open("compiled/%s/traceroute.csv" % (setid), 'w')
  f.write('IP,'+','.join(datasets)+"\n")

  ipset=Set()
  for result in results:
    for item in result:
      ipset.add(item)

  allips=sorted(list(ipset))

  for ip in allips:
    checks=[ip]
    for result in results:
      if ip in result:
        checks.append(1)
      else:
        checks.append(0)
    f.write(','.join(map(str,checks))+"\n")

  f.close()

def parseTraceroute(dataset):
  print("... from %s" % (dataset))
  if not os.path.exists("analysis/%s/traceroute.csv" % (dataset)):
    return None
  f=open("analysis/%s/traceroute.csv" % (dataset))
  ips=map(getIP,f.readlines()[1:])
  f.close()
  return ips

def getIP(line):
  return line.split(',')[1]

def compileNose(setid, datasets, prot):
  print("   compiling "+prot)

  if prot=='http':
    results=map(parseHttpResults, datasets)
  elif prot=='https':
    results=map(parseHttpsResults, datasets)
  else:
    print('Unknown protocol '+prot)
    return

#  datasets, results=filterBothWith(datasets, results, notNone)
  results=filter(notNone, results)
  if len(results)==0:
    return

  f=open("compiled/%s/generate-%s.csv" % (setid, prot), 'w')
  f.write(','.join(datasets)+"\n")

  maxlen=max(map(len, results))

  for x in range(len(results)):
    results[x]=fill(results[x], 'NA', maxlen)

  rows=[]
  for x in range(maxlen):
    row=[]
    for result in results:
      item=str(result[x])
      row.append(item)
    rows.append(row)

  for row in rows:
    f.write(','.join(row)+"\n")

  f.close()

def fill(a, c, maxLen):
  return a + [c]*(maxLen - len(a))

def parseHttpResults(dataset):
  print("... from %s" % (dataset))
  if not os.path.exists("analysis/%s/generate-http.csv" % (dataset)):
    return None
  f=open("analysis/%s/generate-http.csv" % (dataset))
  results=map(bool,f.readlines()[1:])
  f.close()
  return results

def parseHttpsResults(dataset):
  print("... from %s" % (dataset))
  if not os.path.exists("analysis/%s/generate-https.csv" % (dataset)):
    return None
  f=open("analysis/%s/generate-https.csv" % (dataset))
  results=map(bool,f.readlines()[1:])
  f.close()
  return results

def compileSizes(setid, datasets):
  print("   compiling dust_replay_http")

  results=map(parseSizes, datasets)
  datasets, results=filterBothWith(datasets, results, notNone)
  if len(results)==0:
    return

  f=open("compiled/%s/generate-dust_replay_http.csv" % (setid), 'w')
  f.write(','.join(datasets)+"\n")

  f.write(','.join(results)+"\n")

  f.close()

def parseSizes(dataset):
  print("... from %s" % (dataset))
  if os.path.exists("analysis/%s/generate-dust_replay_http.csv" % (dataset)):
    f=open("analysis/%s/generate-dust_replay_http.csv" % (dataset))
    result=f.readlines()[1].strip()
    f.close()
    return result
  else:
    return None
