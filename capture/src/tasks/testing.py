import os
import sys
import glob
import time
import json
import shutil

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
    captureDevice='eth0'
  )
)

@task
def all(options):
  safe_task('traceroute', options)
  safe_task('ping', options)
  safe_task('nmap', options)
  safe_task('capture_http', options)
  safe_task('capture_https', options)
  safe_task('postprocess', options)

def safe_task(name, options):
  try:
    call_task(name)
  except Exception, e:
    print("Error running task %s: %s" % (name, str(e)))

# Record traceroute to server
@task
def traceroute(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; traceroute %s 2>&1 | tee %s/traceroute.txt) &" % (options.testing.traceHost, traceDir))
  time.sleep(30)
  sh('killall traceroute')

# Record ping to server
@task
def ping(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; ping %s 2>&1 | tee %s/ping.txt) &" % (options.testing.traceHost, traceDir))
  time.sleep(60)
  sh('killall ping')

# Check which ports are open on the testing server
@task
def nmap(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("sudo nmap %s 2>&1 | tee %s/nmap.txt" % (options.testing.traceHost, traceDir))

# Package the results for sending
@task
def postprocess(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    print('No results found to postprocess')
  else:
    sh("FILENAME=`date '+%%s'`; zip -9 $FILENAME %s/*; scp $FILENAME.zip against@%s:$FILENAME.zip; echo \"A file called $FILENAME.zip has been created. Please email this file to brandon@blanu.net.\"" % (traceDir, options.testing.traceHost))

# Generate HTTP
@task
def generate_http(options):
  traceDir=options.testing.traceDir
  sh("nosetests generate:HttpTests 2>&1 | tee %s/generate-http.txt" % (traceDir))

# Generate HTTPS traffic
@task
def generate_https(options):
  traceDir=options.testing.traceDir
  sh("nosetests generate:HttpsTests 2>&1 | tee %s/generate-https.txt" % (traceDir))

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

  sh('touch CAPTURE_RUNNING')
  sh("sudo src/capture.py %s %s/%s-%s.pcap &" % (captureDevice, str(traceDir), str(target), str(timestamp())))

  call_task("generate_%s" % (target))

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)

# Test SSH
@task
def ssh(options):
  if os.path.exists('ssh-testfile.txt'):
    os.delete('ssh-testfile.txt')
  try:
    sh("scp brandon@%s:testfile.txt testfile.txt 2>&1 | tee %s/ssh-results.txt" % (options.testing.traceHost, options.testing.traceDir))
  except:
    pass
  if os.path.exists('ssh-testfile.txt'):
    print('SSH SUCCESS')
    os.delete('ssh-testfile.txt')
  else:
    print('SSH FAILURE')

