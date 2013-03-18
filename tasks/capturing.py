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
    traceDir='test'
  ),
  # Capture configuration for HTTPS
  task=Bunch(
    capturing=Bunch(
      capture_https=Bunch(
        # default trace directory
        traceDir='test'
      )
    )
  ),
  # Capture configuration for obfs2
  capture_obfsproxy=Bunch(
    # default trace directory
    traceDir='test'
  ),
  # Capture configuration for Dust
  capture_dust=Bunch(
    # default trace directory
    traceDir='test'
  )
)

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
  if not os.path.exists('traces/'+traceDir):
    os.mkdir('traces/'+traceDir)

  sh('touch CAPTURE_RUNNING')
  sh('sudo ./capture.py eth1 traces/'+str(traceDir)+'/obfsproxy.pcap &')

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
  if not os.path.exists('traces/'+traceDir):
    os.mkdir('traces/'+traceDir)

  sh('touch CAPTURE_RUNNING')
  sh('sudo ./capture.py wlan0 traces/'+str(traceDir)+'/dust.pcap &')

  call_task('run_dust')

  call_task('generate_http_dust')

  call_task('kill_dust')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)

# Capture HTTPS traffic into traces in the specified directory
@task
@cmdopts([
  ('traceDir=', 'd', 'Directory in which to output traces')
])
def capture_https(options):
  traceDir=options.capture_https.traceDir
  if not os.path.exists('traces/'+traceDir):
    os.mkdir('traces/'+traceDir)

  sh('touch CAPTURE_RUNNING')
  sh('sudo ./capture.py eth1 traces/'+str(traceDir)+'/https.pcap &')

  call_task('generate_https')

  sh('rm CAPTURE_RUNNING')
  time.sleep(11)
