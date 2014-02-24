# pavement.py is the config file for paver.
# It contains all of the paver tasks and default options.

import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Options required by different tasks
options(
  # Capture configuration
  capture=Bunch(
    traceDir='traces/test',
    captureDevice='wlan1'
  ),
  # Capture configuration for HTTPS
  task=Bunch(
    capturing=Bunch(
      capture_https=Bunch(
        # default trace directory
        traceDir='traces/test',
        captureDevice='wlan1'
      ),
      capture_http=Bunch(
        # default trace directory
        traceDir='traces/test',
        captureDevice='wlan1'
      )
    )
  ),
  # Capture configuration for obfs2
  capture_obfsproxy=Bunch(
    # default trace directory
    traceDir='traces/test',
    captureDevice='wlan1'
  ),
  # Capture configuration for Dust
  capture_dust=Bunch(
    # default trace directory
    traceDir='traces/test',
    captureDevice='wlan1'
  )
)

def timestamp():
  import datetime, time
  return str(int(time.mktime(datetime.datetime.now().timetuple())))

# Capture HTTPS, HTTP-Tor-obfs2, and HTTP-Tor-Dust traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces')
])
def capture(options):
  options.capture_https.traceDir=options.capture.traceDir
  call_task('capture_https')

  options.capture_obfsproxy.traceDir=options.capture.traceDir
  call_task('capture_obfsproxy')

  options.capture_dust.traceDir=options.capture.traceDir
  call_task('capture_dust')

  call_task('process')

# Capture HTTP-Tor-obfs2 traffic into traces in the specified directory
@task
@needs(['prepareEncoders'])
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces')
])
def capture_obfsproxy(options):
  traceDir=options.capture_obfsproxy.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)

  sh('touch CAPTURE_RUNNING')
  sh('sudo src/capture.py wlan1 '+str(traceDir)+'/obfsproxy.pcap &')

  call_task('run_obfsproxy')

  call_task('generate_tor_obfs2')

  call_task('kill_obfsproxy')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)

# Capture HTTP-Tor-Dust traffic into traces in the specified directory
@task
@needs(['prepareEncoders'])
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces')
])
def capture_dust(options):
  traceDir=options.capture_dust.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)

  sh('touch CAPTURE_RUNNING')
  sh('sudo src/capture.py wlan0 '+str(traceDir)+'/dust.pcap &')

  call_task('run_dust')

  call_task('generate_http_dust')

  call_task('kill_dust')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)

# Capture HTTP traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces'),
  ('captureDevice=', 'c', 'Device to use for capturing traces')
])
def capture_http(options):
  traceDir=options.capture_http.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  captureDevice=options.capture_http.captureDevice

  sh('touch CAPTURE_RUNNING')
  sh('sudo src/capture.py '+captureDevice+' '+str(traceDir)+'/http-'+timestamp()+'.pcap &')

  call_task('generate_http')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)

# Capture HTTPS traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces'),
  ('captureDevice=', 'c', 'Device to use for capturing traces')
])
def capture_https(options):
  traceDir=options.capture_https.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  captureDevice=options.capture_https.captureDevice

  sh('touch CAPTURE_RUNNING')
  sh('sudo src/capture.py '+captureDevice+' '+str(traceDir)+'/https-'+timestamp()+'.pcap &')

  call_task('generate_https')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)
