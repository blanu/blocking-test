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
    captureDevice='eth1'
  )
)

@task
def all(options):
  safe_task('traceroute', options)
  safe_task('ping', options)
  safe_task('nmap', options)
  safe_task('capture_http', options)
  safe_task('capture_https', options)
  safe_task('replay_http', options)
  safe_task('postprocess', options)

def safe_task(name, options):
  print("Execuring task %s. Please wait." % (name))
  try:
    call_task(name)
    print("Task %s completed successfully" % (name))
  except Exception, e:
    print("Error running task %s: %s" % (name, str(e)))
  print('')

def qsh(command):
  sh(command+' >>traces/tasklog.txt')

# Record traceroute to server
@task
def traceroute(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; traceroute %s 2>&1 | tee %s/traceroute.txt) >>traces/tasklog.txt &" % (options.testing.traceHost, traceDir))
  time.sleep(30)
  qsh('killall traceroute')

# Record ping to server
@task
def ping(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; ping %s 2>&1 | tee %s/ping.txt) >>traces/tasklog.txt &" % (options.testing.traceHost, traceDir))
  time.sleep(60)
  qsh('killall ping')

# Check which ports are open on the testing server
@task
def nmap(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  qsh("sudo nmap %s 2>&1 | tee %s/nmap.txt" % (options.testing.traceHost, traceDir))

# Package the results for sending
@task
def postprocess(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    print('No results found to postprocess')
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
  ('captureDevice=', 'c', 'Device to use for capturing traces')
])
def capture_http(options):
  capture(options.testing.traceDir, options.testing.captureDevice, 'http')

# Capture HTTPS traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces'),
  ('captureDevice=', 'c', 'Device to use for capturing traces')
])
def capture_https(options):
  capture(options.testing.traceDir, options.testing.captureDevice, 'https')

def capture(traceDir, captureDevice, target):
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)

  qsh('touch CAPTURE_RUNNING')
  qsh("sudo src/capture.py %s %s/%s-%s.pcap &" % (captureDevice, str(traceDir), str(target), str(timestamp())))

  safe_task("generate_%s" % (target), None)

  qsh('rm CAPTURE_RUNNING')
  time.sleep(11)

def capture_dust_replay_http(traceDir, captureDevice, target):
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)

  qsh('touch CAPTURE_RUNNING')
  qsh("sudo src/capture.py %s %s/%s-%s.pcap &" % (captureDevice, str(traceDir), str(target), str(timestamp())))

  safe_task("generate_dust_replay_http", None)

  qsh('rm CAPTURE_RUNNING')
  time.sleep(11)

@task
def generate_dust_replay_http(options):
  safe_task('replay_http', options)

  time.sleep(30)

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
  sh('~/.cabal/bin/replay-client models/http.ps &')

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
