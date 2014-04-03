import os
import sys
import glob
import time
import json
import shutil
import thread

from paver.easy import *
from paver.path import *

from capturing import timestamp

sys.path.append(os.path.abspath('.'))

# Dependencies:
# - ping
# - traceroute
# - nmap

# Options required by different tasks
options(
  # Capture configuration
  testing=Bunch(
    traceDir='traces',
    traceHost='162.209.102.232',
  )
)

@task
def all(options):
  safe_task('configure', options)
  safe_task('traceroute', options)
  safe_task('ping', options)
  safe_task('nmap', options)
  safe_task('capture_http', options)
  safe_task('capture_https', options)
  safe_task('capture_dust_replay_http', options)
  safe_task('postprocess', options)

def safe_task(name, options):
  print("Executing task %s. Please wait." % (name))
  try:
    call_task(name)
    print("Task %s completed successfully" % (name))
  except Exception, e:
    print("Error running task %s: %s" % (name, str(e)))
  print('')

def qsh(command):
  sh(command+' >>traces/tasklog.txt')

@task
def sanity(options):
  home=os.getenv('HOME')
  if os.path.exists(home+'/.ssh/id_rsa.pub'):
    f=open(home+'/.ssh/id_rsa.pub')
    homekey=f.read()
    f.close()
  else:
    print('Sanity check failure. No SSH key for user account.')
    homekey=None

  if not os.path.exists(home+'/.ssh/config'):
    print('Sanity check failure. No SSH config for user account.')

  if os.path.exists('/root/.ssh/id_rsa.pub'):
    f=open('/root/.ssh/id_rsa.pub')
    rootkey=f.read()
    f.close()
  else:
    print('Sanity check failure. No SSH key for root account.')
    rootkey=None

  if homekey and rootkey:
    if homekey!=rootkey:
      print('Sanity check failure. SSH keys for user and root accounts differ.')

  if homekey:
    sanityfile=options.testing.traceDir+'/sanity1.txt'
    if os.path.exists(sanityfile):
      os.remove(sanityfile)
    sh('ssh against@%s "echo testing" >%s' % (options.testing.traceHost, sanityfile))
    if os.path.exists(sanityfile):
      f=open(sanityfile)
      line=f.read().strip()
      if line!='testing':
        print('Sanity check failure. SSH from user account produced unexpected output.')
    else:
      print('Sanity check failure. SSH from user account produced no output.')

  if rootkey:
    sanityfile=options.testing.traceDir+'/sanity2.txt'
    if os.path.exists(sanityfile):
      os.remove(sanityfile)
    sh('sudo ssh against@%s "echo testing" >%s' % (options.testing.traceHost, sanityfile))
    if os.path.exists(sanityfile):
      f=open(sanityfile)
      line=f.read().strip()
      if line!='testing':
        print('Sanity check failure. SSH from root account produced unexpected output.')
    else:
      print('Sanity check failure. SSH from root account produced no output.')

@task
def configure(options):
  country=raw_input("Enter the country where you are conducting this test: ")
  network=raw_input("Enter the type of network (home, business, academic, etc.): ")
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh('ifconfig | tee %s/ifconfig.txt' % (traceDir))
  f=open(traceDir+'/ifconfig.txt')
  lines=f.readlines()
  f.close()

  devices=set([])
  for line in lines:
    if line[0]!='\t' and line[0]!=' ':
      if ':' in line:
        line=line.split(':')[0]
      if ' ' in line:
        line=line.split(' ')[0]
      devices.add(line)
  print('Detected network devices: '+str(list(devices)))
  if 'wlan1' in devices:
    prefDev='wlan1'
  elif 'eth1' in devices:
    prefDev='eth1'
  elif 'eth0' in devices:
    prefDev='eth0'
  else:
    prefDev='None'
  if prefDev=='None':
    print('No known devices found. Packet capture will not work.')
  else:
    print('Using preferred device %s for packet capture.' % (prefDev))
  f=open(traceDir+'/options.config', 'w')
  f.write(country+"\n")
  f.write(network+"\n")
  f.write(prefDev+"\n")
  f.close()

# Record traceroute to server
@task
def traceroute(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; traceroute %s 2>&1 | tee %s/traceroute.txt) >>traces/tasklog.txt &" % (options.testing.traceHost, traceDir))
  time.sleep(60)
  qsh('killall traceroute')

# Record ping to server
@task
def ping(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; ping -c 25 %s 2>&1 | tee %s/ping.txt) >>traces/tasklog.txt &" % (options.testing.traceHost, traceDir))
  time.sleep(60)
  qsh('killall ping')

# Check which ports are open on the testing server
@task
def nmap(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  qsh("sudo nmap %s 2>&1 | tee %s/nmap.txt" % (options.testing.traceHost, traceDir))

def sanitize(s):
  result=''
  for letter in s.lower():
    if letter>='a' and letter<='z':
      result=result+letter
  return result

# Package the results for sending
@task
def postprocess(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    print('No results found to postprocess')
  else:
    if os.path.exists(traceDir+'/options.config'):
      f=open(traceDir+'/options.config')
      country=sanitize(f.readline().strip())
      network=f.readline().strip()
      qsh("TRACES=%s; FILENAME=%s-`date '+%%s'`; LOCALPATH=$HOME/Desktop/$FILENAME; zip -9 $LOCALPATH $TRACES/*; scp $LOCALPATH.zip against@%s:$FILENAME.zip; echo \"A file called $LOCALPATH.zip has been created.\"; rm $TRACES/*" % (traceDir, country, options.testing.traceHost))
    else:
      qsh("TRACES=%s; FILENAME=`date '+%%s'`; LOCALPATH=$HOME/Desktop/$FILENAME; zip -9 $LOCALPATH $TRACES/*; scp $LOCALPATH.zip against@%s:$FILENAME.zip; echo \"A file called $LOCALPATH.zip has been created.\"; rm $TRACES/*" % (traceDir, options.testing.traceHost))

# Generate HTTP
@task
def generate_http(options):
  traceDir=options.testing.traceDir
  qsh("nosetests generate:HttpTests 2>&1 | tee %s/generate-http.txt" % (traceDir))

# Generate HTTPS traffic
@task
def generate_https(options):
  traceDir=options.testing.traceDir
  qsh("nosetests generate:HttpsTests 2>&1 | tee %s/generate-https.txt" % (traceDir))

# Capture HTTP traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces'),
])
def capture_http(options):
  capture(options.testing.traceDir, 'http')

# Capture HTTPS traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces'),
])
def capture_https(options):
  capture(options.testing.traceDir, 'https')

def capture(traceDir, target):
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)

  f=open(traceDir+'/options.config')
  lines=f.readlines()
  f.close()
  if len(lines)<3 or lines[2].strip()=='None':
    print('No device configuration, defaulting to wlan1')
    captureDevice='wlan1'
  else:
    captureDevice=lines[2].strip()
    print('Detected preferred network device '+captureDevice)

  qsh('touch CAPTURE_RUNNING')
  qsh("sudo src/capture.py %s %s/%s-%s.pcap &" % (captureDevice, str(traceDir), str(target), str(timestamp())))

  safe_task("generate_%s" % (target), None)

  qsh('rm CAPTURE_RUNNING')
  time.sleep(11)

@task
def capture_dust_replay_http(options):
  capture(options.testing.traceDir, options.testing.captureDevice, 'dust_replay_http')

@task
def generate_dust_replay_http(options):
  safe_task('replay_http', options)

  time.sleep(60)

  safe_task('kill_dust_replay_http', options)

# Test SSH
@task
def ssh(options):
  if os.path.exists('ssh-testfile.txt'):
    os.delete('ssh-testfile.txt')
  try:
    qsh("scp brandon@%s:testfile.txt testfile.txt 2>&1 | tee %s/ssh-results.txt" % (options.testing.traceHost, options.testing.traceDir))
  except:
    pass
  if os.path.exists('ssh-testfile.txt'):
    print('SSH SUCCESS')
    os.delete('ssh-testfile.txt')
  else:
    print('SSH FAILURE')

@task
def replay_http(options):
  safe_task('run_remote_dust_replay_http_server', options)
  time.sleep(5)
  safe_task('run_local_dust_replay_http_client', options)
  time.sleep(5)

@task
def run_remote_dust_replay_http_server(options):
  sh('fab -f src/fabfile.py -H against@162.209.102.232 run_dust_replay_http_server &')

@task
def run_local_dust_replay_http_server(options):
  sh('nohup ~/.cabal/bin/replay-server models/http.ps &')

@task
def run_local_dust_replay_http_client(options):
  sh('~/blocking-test/capture/bin/replay-client models/http.ps')

@task
def kill_dust_replay_http(options):
  safe_task('kill_local_dust_replay_http_client', options)
  safe_task('kill_remote_dust_replay_http_server', options)

@task
def kill_remote_dust_replay_http_server(options):
  sh('fab -f src/fabfile.py -H against@162.209.102.232 kill_dust_replay_http_server')

@task
def kill_local_dust_replay_http_client(options):
  sh('killall replay-client')

@task
def kill_local_dust_replay_http_server(options):
  sh('killall replay-server')
