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
    traceHost='internews.org',
    captureDevice='eth0'
  )
)

@task
def all(options):
  call_task('traceroute')
  call_task('ping')
  call_task('nmap')
  call_task('postprocess')

# Record traceroute to server
@task
def traceroute(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; traceroute %s 2>&1 | tee %s/traceroute.txt) &" % (options.testing.traceHost, traceDir))
  time.sleep(180)
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
    sh("FILENAME=`date '+%%s'`; zip -9 $FILENAME %s/*" % (traceDir))

# Generate HTTP
@task
def generate_http(options):
  traceDir=options.generate.traceDir
  sh("nosetests generate:HttpTests 2>&1 | tee %s/generate-http.txt" % (traceDir))

# Generate HTTPS traffic
@task
def generate_https(options):
  traceDir=options.generate.traceDir
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
